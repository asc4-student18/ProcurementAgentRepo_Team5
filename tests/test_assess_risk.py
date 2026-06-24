from tools.assess_risk import assess_risk


def test_assess_risk_low_for_active_unflagged_vendor() -> None:
    result = assess_risk("V-001")

    assert result["vendor_id"] == "V-001"
    assert result["compliance_flag"] is False
    assert result["contract_status"] == "active"
    assert result["risk_level"] == "low"


def test_assess_risk_medium_for_no_contract_vendor() -> None:
    result = assess_risk("V-004")

    assert result["compliance_flag"] is False
    assert result["contract_status"] == "none"
    assert result["risk_level"] == "medium"


def test_assess_risk_high_for_expired_contract_vendor() -> None:
    result = assess_risk("V-010")

    assert result["compliance_flag"] is False
    assert result["contract_status"] == "expired"
    assert result["risk_level"] == "high"


def test_assess_risk_critical_for_compliance_flagged_vendor() -> None:
    result = assess_risk("V-006")

    assert result["compliance_flag"] is True
    assert result["contract_status"] == "active"
    assert result["risk_level"] == "critical"


def test_assess_risk_unknown_vendor_raises_value_error() -> None:
    result = assess_risk("V-999")

    assert result["vendor_id"] == "V-999"
    assert result["risk_level"] == "unknown"
    assert result["error"] is not None
    assert result["error"]["code"] == "VENDOR_NOT_FOUND"
