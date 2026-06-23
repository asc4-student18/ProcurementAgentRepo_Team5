from tools.budget import check_budget


def test_check_budget_within_and_over_budget_for_cc003() -> None:
    within_result = check_budget(cost_center_id="CC-003", requested_amount=6900.0)
    over_result = check_budget(cost_center_id="CC-003", requested_amount=7000.0)

    assert within_result["within_budget"] is True
    assert within_result["remaining_budget"] == 6900.0
    assert within_result["overage"] == 0.0
    assert within_result["error"] is None

    assert over_result["within_budget"] is False
    assert over_result["remaining_budget"] == 6900.0
    assert over_result["overage"] == 100.0
    assert over_result["error"] is None
