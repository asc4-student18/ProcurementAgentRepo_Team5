from __future__ import annotations

from typing import Any

from tools.policy_compliance import check_policy_compliance as _check_policy_compliance


def check_policy_compliance(
    purchase_request: dict[str, Any],
) -> dict[str, Any]:
    """Backward-compatible wrapper for policy compliance checks."""

    return _check_policy_compliance(purchase_request)
