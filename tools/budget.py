from __future__ import annotations

from typing import Any

from data.loader import load_budgets


def check_budget(cost_center_id: str, requested_amount: float) -> dict[str, Any]:
    """Evaluate whether a requested amount fits the remaining budget for a cost center.

    Args:
        cost_center_id: Cost center identifier to evaluate.
        requested_amount: Amount requested for purchase approval.

    Returns:
        A dictionary containing:
        - within_budget: True when requested_amount is within remaining budget.
        - remaining_budget: Remaining budget for the matched cost center.
        - overage: 0.0 when within budget, otherwise the amount above remaining budget.
        - error: None on success; structured lookup failure details when not found.
    """

    budgets = load_budgets()
    match = next(
        (item for item in budgets if str(item.get("cost_center_id", "")) == cost_center_id),
        None,
    )

    if match is None:
        return {
            "within_budget": False,
            "remaining_budget": None,
            "overage": None,
            "error": {
                "code": "COST_CENTER_NOT_FOUND",
                "message": f"Unknown cost center: {cost_center_id}",
            },
        }

    remaining_budget = float(match.get("remaining", 0.0))
    within_budget = requested_amount <= remaining_budget
    overage = 0.0 if within_budget else requested_amount - remaining_budget

    return {
        "within_budget": within_budget,
        "remaining_budget": remaining_budget,
        "overage": overage,
        "error": None,
    }
