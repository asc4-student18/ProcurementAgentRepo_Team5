from __future__ import annotations

from typing import Any

from data import loader


def _error_result(code: str, message: str) -> dict[str, Any]:
    return {
        "within_budget": False,
        "remaining_budget": None,
        "overage": None,
        "error": {
            "code": code,
            "message": message,
        },
    }


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

    try:
        budgets = loader.load_budgets()
    except FileNotFoundError as exc:
        return _error_result("DATA_FILE_NOT_FOUND", f"Data loading failure: {exc}")
    except KeyError as exc:
        return _error_result("DATA_SCHEMA_ERROR", f"Data schema failure: missing key {exc}")
    except Exception as exc:
        return _error_result("BUDGET_CHECK_ERROR", f"Unexpected budget check failure: {exc}")

    match = next(
        (item for item in budgets if str(item.get("cost_center_id", "")) == cost_center_id),
        None,
    )

    if match is None:
        return _error_result(
            "COST_CENTER_NOT_FOUND",
            f"Unknown cost center: {cost_center_id}",
        )

    remaining_budget = float(match.get("remaining", 0.0))
    within_budget = requested_amount <= remaining_budget
    overage = 0.0 if within_budget else requested_amount - remaining_budget

    return {
        "within_budget": within_budget,
        "remaining_budget": remaining_budget,
        "overage": overage,
        "error": None,
    }
