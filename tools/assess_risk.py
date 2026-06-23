from __future__ import annotations

from data.loader import load_vendors
from models import VendorRiskProfile


def _compute_risk_level(compliance_flag: bool, contract_status: str) -> str:
    if compliance_flag:
        return "critical"
    if contract_status == "expired":
        return "high"
    if contract_status == "none":
        return "medium"
    return "low"


def assess_risk(vendor_id: str) -> VendorRiskProfile:
    vendors = load_vendors()
    vendor = next((item for item in vendors if item.get("vendor_id") == vendor_id), None)

    if vendor is None:
        raise ValueError(f"Unknown vendor_id: {vendor_id}")

    compliance_flag = bool(vendor.get("compliance_flag", False))
    contract_status = str(vendor.get("contract_status", "none")).strip().lower()
    risk_level = _compute_risk_level(compliance_flag=compliance_flag, contract_status=contract_status)

    return VendorRiskProfile(
        vendor_id=vendor_id,
        compliance_flag=compliance_flag,
        contract_status=contract_status,
        risk_level=risk_level,
    )
