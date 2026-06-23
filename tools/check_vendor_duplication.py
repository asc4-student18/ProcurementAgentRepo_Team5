from __future__ import annotations

from typing import Any

from tools.vendor_duplication import check_vendor_duplication as _check_vendor_duplication


def check_vendor_duplication(
    vendor_id: str,
    purchase_category: str,
    total_amount: float | None = None,
) -> dict[str, Any]:
    """Backward-compatible wrapper for vendor duplication checks."""

    return _check_vendor_duplication(
        vendor_id=vendor_id,
        purchase_category=purchase_category,
        total_amount=total_amount,
    )
