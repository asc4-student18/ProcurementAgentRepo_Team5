from __future__ import annotations

from typing import Any

from data import loader


def _error_result(vendor_id: str, purchase_category: str | None, code: str, message: str) -> dict[str, Any]:
    return {
        "requested_vendor_id": vendor_id,
        "purchase_category": (purchase_category or "").strip().lower(),
        "policy_id": "POL-001",
        "threshold_amount": None,
        "has_active_contract_conflict": False,
        "deny_triggered": False,
        "conflicting_vendor_ids": [],
        "conflicting_contracts": [],
        "message": "Vendor duplication check failed.",
        "error": {
            "code": code,
            "message": message,
        },
    }


def _get_pol001() -> tuple[float, set[str]]:
    """Return POL-001 threshold and affected categories."""

    policies = loader.load_policies()
    for policy in policies:
        if policy.get("policy_id") == "POL-001":
            threshold = float(policy.get("threshold_amount", 25000.0))
            categories = {
                str(item).strip().lower()
                for item in policy.get("affected_categories", [])
                if str(item).strip()
            }
            return threshold, categories
    return 25000.0, set()


def check_vendor_duplication(
    vendor_id: str,
    purchase_category: str | None = None,
    total_amount: float | None = None,
    *,
    category: str | None = None,
    requested_amount: float | None = None,
) -> dict[str, Any]:
    """Check for active contracted vendor conflicts under POL-001 rules.

    Args:
        vendor_id: Requested vendor identifier.
        purchase_category: Purchase category to evaluate.
        total_amount: Optional requested amount used for POL-001 deny gating.
        category: Backward-compatible alias for purchase_category.
        requested_amount: Backward-compatible alias for total_amount.

    Returns:
        Structured result with conflict details and threshold logic outcome:
        - requested_vendor_id
        - purchase_category
        - policy_id
        - threshold_amount
        - has_active_contract_conflict
        - deny_triggered
        - conflicting_vendor_ids
        - conflicting_contracts
        - message
    """

    effective_category = purchase_category if purchase_category is not None else category
    if effective_category is None:
        return _error_result(
            vendor_id,
            effective_category,
            "MISSING_CATEGORY",
            "purchase_category is required",
        )

    normalized_category = effective_category.strip().lower()

    try:
        effective_amount = total_amount if total_amount is not None else requested_amount
        vendors = loader.load_vendors()
        threshold_amount, affected_categories = _get_pol001()
    except FileNotFoundError as exc:
        return _error_result(
            vendor_id,
            effective_category,
            "DATA_FILE_NOT_FOUND",
            f"Data loading failure: {exc}",
        )
    except KeyError as exc:
        return _error_result(
            vendor_id,
            effective_category,
            "DATA_SCHEMA_ERROR",
            f"Data schema failure: missing key {exc}",
        )
    except Exception as exc:
        return _error_result(
            vendor_id,
            effective_category,
            "VENDOR_DUPLICATION_ERROR",
            f"Unexpected vendor duplication failure: {exc}",
        )

    requested_vendor = next(
        (item for item in vendors if str(item.get("vendor_id", "")) == vendor_id),
        None,
    )
    requested_is_active_for_category = bool(
        requested_vendor
        and str(requested_vendor.get("category", "")).strip().lower() == normalized_category
        and str(requested_vendor.get("contract_status", "")).strip().lower() == "active"
    )

    conflicting_contracts = [
        {
            "vendor_id": str(item.get("vendor_id", "")),
            "vendor_name": str(item.get("name", "")),
            "category": str(item.get("category", "")),
            "contract_id": str(item.get("contract_id", "")),
            "contract_status": str(item.get("contract_status", "")),
        }
        for item in vendors
        if str(item.get("vendor_id", "")) != vendor_id
        and str(item.get("category", "")).strip().lower() == normalized_category
        and str(item.get("contract_status", "")).strip().lower() == "active"
    ]

    has_active_contract_conflict = len(conflicting_contracts) > 0
    category_is_contracted = normalized_category in affected_categories
    threshold_triggered = (
        effective_amount is not None and float(effective_amount) >= float(threshold_amount)
    )
    deny_triggered = bool(
        has_active_contract_conflict
        and category_is_contracted
        and threshold_triggered
        and not requested_is_active_for_category
    )

    if not has_active_contract_conflict:
        message = "No active contract conflicts found for this category."
    elif deny_triggered:
        message = "POL-001 threshold logic triggered denial for vendor duplication conflict."
    else:
        message = "Conflict found, but POL-001 deny criteria were not fully met."

    return {
        "requested_vendor_id": vendor_id,
        "purchase_category": normalized_category,
        "policy_id": "POL-001",
        "threshold_amount": threshold_amount,
        "has_active_contract_conflict": has_active_contract_conflict,
        "deny_triggered": deny_triggered,
        "conflicting_vendor_ids": [item["vendor_id"] for item in conflicting_contracts],
        "conflicting_contracts": conflicting_contracts,
        "message": message,
        "error": None,
    }
