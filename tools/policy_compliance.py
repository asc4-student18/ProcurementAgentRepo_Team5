from __future__ import annotations

from typing import Any

from data import loader
from models import PurchaseRequest


def _error_result(code: str, message: str) -> dict[str, Any]:
    return {
        "violations": [],
        "evaluated_policy_ids": [
            "POL-001",
            "POL-002",
            "POL-003",
            "POL-004",
            "POL-005",
            "POL-006",
            "POL-007",
            "POL-008",
        ],
        "error": {
            "code": code,
            "message": message,
        },
    }


def check_policy_compliance(
    purchase_request: PurchaseRequest | dict[str, Any],
) -> dict[str, Any]:
    """Evaluate a purchase request against POL-001 through POL-008.

    Args:
        purchase_request: PurchaseRequest model or request dictionary.

    Returns:
        A dictionary containing:
        - violations: list of policy violations with policy_id, rule_violated, forced_decision.
        - evaluated_policy_ids: list of evaluated policy IDs (POL-001..POL-008).
    """

    request_data = (
        purchase_request.model_dump()
        if isinstance(purchase_request, PurchaseRequest)
        else purchase_request
    )

    try:
        policies = loader.load_policies()
        vendors = loader.load_vendors()
        budgets = loader.load_budgets()
    except FileNotFoundError as exc:
        return _error_result("DATA_FILE_NOT_FOUND", f"Data loading failure: {exc}")
    except KeyError as exc:
        return _error_result("DATA_SCHEMA_ERROR", f"Data schema failure: missing key {exc}")
    except Exception as exc:
        return _error_result("POLICY_COMPLIANCE_ERROR", f"Unexpected policy check failure: {exc}")

    vendor_id = str(request_data.get("vendor_id", "")).strip()
    category = str(request_data.get("category", "")).strip().lower()
    cost_center_id = str(request_data.get("cost_center_id", "")).strip()
    total_amount = float(request_data.get("total_amount", 0.0))
    quantity = float(request_data.get("quantity", 0.0))
    manager_approved = bool(request_data.get("manager_approved", True))
    director_approved = bool(request_data.get("director_approved", False))

    policy_index = {str(policy.get("policy_id", "")): policy for policy in policies}
    vendor = next((item for item in vendors if item.get("vendor_id") == vendor_id), None)
    budget = next((item for item in budgets if item.get("cost_center_id") == cost_center_id), None)

    violations: list[dict[str, str]] = []

    pol_001 = policy_index.get("POL-001", {})
    pol_001_threshold = float(pol_001.get("threshold_amount", 25000.0))
    pol_001_categories = {
        str(item).lower() for item in pol_001.get("affected_categories", [])
    }
    active_in_category = [
        item
        for item in vendors
        if str(item.get("category", "")).lower() == category
        and str(item.get("contract_status", "")).lower() == "active"
    ]
    requested_is_active_for_category = bool(
        vendor
        and str(vendor.get("contract_status", "")).lower() == "active"
        and str(vendor.get("category", "")).lower() == category
    )
    if (
        category in pol_001_categories
        and total_amount >= pol_001_threshold
        and active_in_category
        and not requested_is_active_for_category
    ):
        violations.append(
            {
                "policy_id": "POL-001",
                "rule_violated": str(
                    pol_001.get("description", "Single-source restriction violated.")
                ),
                "forced_decision": "deny",
            }
        )

    pol_002 = policy_index.get("POL-002", {})
    pol_002_lower = float(pol_002.get("threshold_amount", 10000.0))
    pol_002_upper = float(pol_002.get("upper_threshold", 49999.99))
    if pol_002_lower <= total_amount <= pol_002_upper and not manager_approved:
        violations.append(
            {
                "policy_id": "POL-002",
                "rule_violated": str(
                    pol_002.get("description", "Manager approval threshold violated.")
                ),
                "forced_decision": "escalate",
            }
        )

    pol_003 = policy_index.get("POL-003", {})
    pol_003_threshold = float(pol_003.get("threshold_amount", 50000.0))
    if total_amount >= pol_003_threshold and not director_approved:
        violations.append(
            {
                "policy_id": "POL-003",
                "rule_violated": str(
                    pol_003.get("description", "Director approval threshold violated.")
                ),
                "forced_decision": "escalate",
            }
        )

    pol_004 = policy_index.get("POL-004", {})
    pol_004_categories = {
        str(item).lower() for item in pol_004.get("affected_categories", [])
    }
    if category in pol_004_categories:
        violations.append(
            {
                "policy_id": "POL-004",
                "rule_violated": str(pol_004.get("description", "Prohibited category violated.")),
                "forced_decision": "deny",
            }
        )

    pol_005 = policy_index.get("POL-005", {})
    if vendor and str(vendor.get("contract_status", "")).lower() == "expired":
        violations.append(
            {
                "policy_id": "POL-005",
                "rule_violated": str(
                    pol_005.get("description", "Expired contract vendor violated.")
                ),
                "forced_decision": "deny",
            }
        )

    pol_006 = policy_index.get("POL-006", {})
    if vendor and bool(vendor.get("compliance_flag", False)):
        violations.append(
            {
                "policy_id": "POL-006",
                "rule_violated": str(
                    pol_006.get("description", "Compliance-flagged vendor hold violated.")
                ),
                "forced_decision": "escalate",
            }
        )

    pol_007 = policy_index.get("POL-007", {})
    requested_is_active_staffing_vendor = bool(
        vendor
        and str(vendor.get("contract_status", "")).lower() == "active"
        and str(vendor.get("category", "")).lower() == "staffing"
    )
    if category == "staffing" and quantity > 40 and not requested_is_active_staffing_vendor:
        violations.append(
            {
                "policy_id": "POL-007",
                "rule_violated": str(
                    pol_007.get("description", "Staffing single-source requirement violated.")
                ),
                "forced_decision": "deny",
            }
        )

    pol_008 = policy_index.get("POL-008", {})
    if budget is not None and total_amount > float(budget.get("remaining", 0.0)):
        violations.append(
            {
                "policy_id": "POL-008",
                "rule_violated": str(pol_008.get("description", "Budget overage violated.")),
                "forced_decision": "deny",
            }
        )

    return {
        "violations": violations,
        "evaluated_policy_ids": [
            "POL-001",
            "POL-002",
            "POL-003",
            "POL-004",
            "POL-005",
            "POL-006",
            "POL-007",
            "POL-008",
        ],
        "error": None,
    }
