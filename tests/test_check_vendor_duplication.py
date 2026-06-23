from tools.check_vendor_duplication import check_vendor_duplication


def test_check_vendor_duplication_triggers_deny_above_threshold() -> None:
    result = check_vendor_duplication(
        vendor_id="V-012",
        purchase_category="office_supplies",
        total_amount=28500.0,
    )

    assert result.has_active_contract_conflict is True
    assert set(result.conflicting_vendor_ids) == {"V-001", "V-003"}
    assert result.deny_triggered is True
    assert result.threshold_amount == 25000.0


def test_check_vendor_duplication_no_deny_below_threshold() -> None:
    result = check_vendor_duplication(
        vendor_id="V-012",
        purchase_category="office_supplies",
        total_amount=5000.0,
    )

    assert result.has_active_contract_conflict is True
    assert result.deny_triggered is False


def test_check_vendor_duplication_contracted_vendor_no_deny() -> None:
    result = check_vendor_duplication(
        vendor_id="V-001",
        purchase_category="office_supplies",
        total_amount=40000.0,
    )

    assert result.has_active_contract_conflict is True
    assert "V-003" in result.conflicting_vendor_ids
    assert result.deny_triggered is False


def test_check_vendor_duplication_no_conflict_category() -> None:
    result = check_vendor_duplication(
        vendor_id="V-004",
        purchase_category="courier_services",
        total_amount=30000.0,
    )

    assert result.has_active_contract_conflict is False
    assert result.conflicting_vendor_ids == []
    assert result.deny_triggered is False
