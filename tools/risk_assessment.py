from __future__ import annotations

from typing import Any

from tools.assess_risk import assess_risk as _assess_risk


def assess_risk(vendor_id: str) -> dict[str, Any]:
    """Backward-compatible wrapper for vendor risk assessment."""

    return _assess_risk(vendor_id)
