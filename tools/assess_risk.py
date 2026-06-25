from __future__ import annotations

from typing import Any

from data import loader


def _error_result(vendor_id: str, code: str, message: str) -> dict[str, Any]:
    # Use conservative but valid fallback values so risk_level always remains in
    # the allowed set (low/medium/high/critical) for any vendor ID.
    contract_status = "none"
    compliance_flag = False
    risk_level = _compute_risk_level(compliance_flag=compliance_flag, contract_status=contract_status)
    return {
        "vendor_id": vendor_id,
        "compliance_flag": compliance_flag,
        "contract_status": contract_status,
        "risk_level": risk_level,
        "error": {
            "code": code,
            "message": message,
        },
    }


def _compute_risk_level(compliance_flag: bool, contract_status: str) -> str:
    if compliance_flag:
        return "critical"
    if contract_status == "expired":
        return "high"
    if contract_status == "none":
        return "medium"
    return "low"


def assess_risk(vendor_id: str) -> dict[str, Any]:
    """Assess vendor risk based on compliance and contract status."""

    try:
        vendors = loader.load_vendors()
    except FileNotFoundError as exc:
        return _error_result(vendor_id, "DATA_FILE_NOT_FOUND", f"Data loading failure: {exc}")
    except KeyError as exc:
        return _error_result(vendor_id, "DATA_SCHEMA_ERROR", f"Data schema failure: missing key {exc}")
    except Exception as exc:
        return _error_result(vendor_id, "RISK_ASSESSMENT_ERROR", f"Unexpected risk check failure: {exc}")

    vendor = next((item for item in vendors if item.get("vendor_id") == vendor_id), None)

    if vendor is None:
        return _error_result(vendor_id, "VENDOR_NOT_FOUND", f"Unknown vendor_id: {vendor_id}")

    compliance_flag = bool(vendor.get("compliance_flag", False))
    contract_status = str(vendor.get("contract_status", "none")).strip().lower()
    risk_level = _compute_risk_level(compliance_flag=compliance_flag, contract_status=contract_status)

    return {
        "vendor_id": vendor_id,
        "compliance_flag": compliance_flag,
        "contract_status": contract_status,
        "risk_level": risk_level,
        "error": None,
    }
