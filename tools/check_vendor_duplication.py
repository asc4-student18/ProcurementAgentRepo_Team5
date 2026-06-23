from __future__ import annotations

from models import VendorContractConflict, VendorDuplicationResult
from data.loader import load_policies, load_vendors


def _get_pol001_threshold() -> float:
    policies = load_policies()
    for policy in policies:
        if policy.get("policy_id") == "POL-001":
            threshold = policy.get("threshold_amount", 25000.0)
            return float(threshold)
    return 25000.0


def check_vendor_duplication(
    vendor_id: str,
    purchase_category: str,
    total_amount: float | None = None,
) -> VendorDuplicationResult:
    vendors = load_vendors()
    threshold_amount = _get_pol001_threshold()

    normalized_category = purchase_category.strip().lower()
    requested_vendor = next(
        (vendor for vendor in vendors if vendor.get("vendor_id") == vendor_id),
        None,
    )

    requested_is_contracted = bool(
        requested_vendor
        and str(requested_vendor.get("category", "")).lower() == normalized_category
        and requested_vendor.get("contract_status") == "active"
    )

    conflicting_vendors = [
        vendor
        for vendor in vendors
        if vendor.get("vendor_id") != vendor_id
        and str(vendor.get("category", "")).lower() == normalized_category
        and vendor.get("contract_status") == "active"
    ]

    conflicting_contracts = [
        VendorContractConflict(
            vendor_id=str(vendor.get("vendor_id", "")),
            vendor_name=str(vendor.get("name", "")),
            category=str(vendor.get("category", "")),
            contract_id=str(vendor.get("contract_id", "")),
            contract_status=str(vendor.get("contract_status", "")),
        )
        for vendor in conflicting_vendors
    ]

    has_active_contract_conflict = len(conflicting_contracts) > 0
    amount_triggers_policy = total_amount is not None and total_amount >= threshold_amount

    deny_triggered = bool(
        has_active_contract_conflict and amount_triggers_policy and not requested_is_contracted
    )

    if not has_active_contract_conflict:
        message = "No active contract conflicts found for this category."
    elif deny_triggered:
        message = (
            "Active contracted vendor(s) exist in this category and request meets "
            "POL-001 threshold; deny is triggered."
        )
    else:
        message = (
            "Active contracted vendor(s) exist in this category, but POL-001 deny "
            "criteria are not fully met."
        )

    return VendorDuplicationResult(
        requested_vendor_id=vendor_id,
        purchase_category=normalized_category,
        total_amount=total_amount,
        threshold_amount=threshold_amount,
        has_active_contract_conflict=has_active_contract_conflict,
        deny_triggered=deny_triggered,
        conflicting_vendor_ids=[contract.vendor_id for contract in conflicting_contracts],
        conflicting_contracts=conflicting_contracts,
        message=message,
    )
