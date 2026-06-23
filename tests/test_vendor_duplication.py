from tools.vendor_duplication import check_vendor_duplication


def test_vendor_duplication_req_008_conflicts() -> None:
    """REQ-008: NovaPrint office_supplies at 28,500 should conflict with V-001 and V-003."""

    result = check_vendor_duplication(
        vendor_id="V-012",
        purchase_category="office_supplies",
        total_amount=28500.0,
    )

    assert result["has_active_contract_conflict"] is True
    assert set(result["conflicting_vendor_ids"]) == {"V-001", "V-003"}
    assert result["deny_triggered"] is True
