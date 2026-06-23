from __future__ import annotations

from typing import Any

from data.loader import load_budgets, load_policies, load_vendors
from models import PolicyComplianceResult, PolicyViolation


def _policy_by_id(policies: list[dict[str, Any]], policy_id: str) -> dict[str, Any]:
    for policy in policies:
        if policy.get("policy_id") == policy_id:
            return policy
    raise ValueError(f"Policy {policy_id} not found")


def _vendor_by_id(vendors: list[dict[str, Any]], vendor_id: str) -> dict[str, Any] | None:
    return next((vendor for vendor in vendors if vendor.get("vendor_id") == vendor_id), None)


def _budget_by_cost_center(
    budgets: list[dict[str, Any]], cost_center_id: str
) -> dict[str, Any] | None:
    return next(
        (budget for budget in budgets if budget.get("cost_center_id") == cost_center_id),
        None,
    )


def check_policy_compliance(purchase_request: dict[str, Any]) -> PolicyComplianceResult:
    policies = load_policies()
    vendors = load_vendors()
    budgets = load_budgets()

    vendor_id = str(purchase_request.get("vendor_id", "")).strip()
    category = str(purchase_request.get("category", "")).strip().lower()
    cost_center_id = str(purchase_request.get("cost_center_id", "")).strip()
    total_amount = float(purchase_request.get("total_amount", 0.0))
    quantity = float(purchase_request.get("quantity", 0.0))
    manager_approved = bool(purchase_request.get("manager_approved", False))
    director_approved = bool(purchase_request.get("director_approved", False))

    vendor = _vendor_by_id(vendors, vendor_id)
    budget = _budget_by_cost_center(budgets, cost_center_id)

    violations: list[PolicyViolation] = []

    # POL-001: Single-source restriction over threshold for covered categories.
    pol_001 = _policy_by_id(policies, "POL-001")
    pol_001_threshold = float(pol_001.get("threshold_amount", 25000.0))
    pol_001_categories = {
        str(item).lower() for item in pol_001.get("affected_categories", [])
    }
    active_in_category = [
        candidate
        for candidate in vendors
        if str(candidate.get("category", "")).lower() == category
        and candidate.get("contract_status") == "active"
    ]
    requested_is_active_for_category = bool(
        vendor
        and vendor.get("contract_status") == "active"
        and str(vendor.get("category", "")).lower() == category
    )
    if (
        category in pol_001_categories
        and total_amount > pol_001_threshold
        and len(active_in_category) > 0
        and not requested_is_active_for_category
    ):
        violations.append(
            PolicyViolation(
                policy_id="POL-001",
                rule_violated=pol_001.get("description", "Single-source restriction violated."),
                forced_decision="deny",
            )
        )

    # POL-002: Manager approval threshold.
    pol_002 = _policy_by_id(policies, "POL-002")
    pol_002_lower = float(pol_002.get("threshold_amount", 10000.0))
    pol_002_upper = float(pol_002.get("upper_threshold", 49999.99))
    if pol_002_lower <= total_amount <= pol_002_upper and not manager_approved:
        violations.append(
            PolicyViolation(
                policy_id="POL-002",
                rule_violated=pol_002.get("description", "Manager approval threshold violated."),
                forced_decision="escalate",
            )
        )

    # POL-003: Director approval threshold.
    pol_003 = _policy_by_id(policies, "POL-003")
    pol_003_threshold = float(pol_003.get("threshold_amount", 50000.0))
    if total_amount >= pol_003_threshold and not director_approved:
        violations.append(
            PolicyViolation(
                policy_id="POL-003",
                rule_violated=pol_003.get("description", "Director approval threshold violated."),
                forced_decision="escalate",
            )
        )

    # POL-004: Prohibited category.
    pol_004 = _policy_by_id(policies, "POL-004")
    pol_004_categories = {
        str(item).lower() for item in pol_004.get("affected_categories", [])
    }
    if category in pol_004_categories:
        violations.append(
            PolicyViolation(
                policy_id="POL-004",
                rule_violated=pol_004.get("description", "Prohibited category violated."),
                forced_decision="deny",
            )
        )

    # POL-005: Expired contract vendor.
    pol_005 = _policy_by_id(policies, "POL-005")
    if vendor and vendor.get("contract_status") == "expired":
        violations.append(
            PolicyViolation(
                policy_id="POL-005",
                rule_violated=pol_005.get("description", "Expired contract vendor violated."),
                forced_decision="deny",
            )
        )

    # POL-006: Compliance-flagged vendor hold.
    pol_006 = _policy_by_id(policies, "POL-006")
    if vendor and bool(vendor.get("compliance_flag", False)):
        violations.append(
            PolicyViolation(
                policy_id="POL-006",
                rule_violated=pol_006.get("description", "Compliance-flagged vendor hold violated."),
                forced_decision="escalate",
            )
        )

    # POL-007: Staffing single-source by engagement hours.
    pol_007 = _policy_by_id(policies, "POL-007")
    staffing_category = category == "staffing"
    requested_is_active_staffing_vendor = bool(
        vendor
        and vendor.get("contract_status") == "active"
        and str(vendor.get("category", "")).lower() == "staffing"
    )
    if staffing_category and quantity > 40 and not requested_is_active_staffing_vendor:
        violations.append(
            PolicyViolation(
                policy_id="POL-007",
                rule_violated=pol_007.get(
                    "description", "Staffing single-source requirement violated."
                ),
                forced_decision="deny",
            )
        )

    # POL-008: Budget overage prohibition.
    pol_008 = _policy_by_id(policies, "POL-008")
    if budget is not None:
        remaining = float(budget.get("remaining", 0.0))
        if total_amount > remaining:
            violations.append(
                PolicyViolation(
                    policy_id="POL-008",
                    rule_violated=pol_008.get("description", "Budget overage prohibition violated."),
                    forced_decision="deny",
                )
            )

    return PolicyComplianceResult(
        request_id=(
            str(purchase_request.get("request_id"))
            if purchase_request.get("request_id") is not None
            else None
        ),
        violations=violations,
        evaluated_policy_ids=[
            str(policy.get("policy_id", "")) for policy in policies if policy.get("policy_id")
        ],
    )
