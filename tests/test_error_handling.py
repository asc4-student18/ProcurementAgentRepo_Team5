from __future__ import annotations

from unittest.mock import patch

from agent import generate_recommendation
from models import PurchaseRequest


def test_generate_recommendation_handles_budget_loader_runtime_error() -> None:
    request = PurchaseRequest(
        request_id="REQ-ERR-001",
        requestor="Test User",
        cost_center_id="CC-001",
        vendor_name="BlueSky Cloud Solutions",
        vendor_id="V-002",
        category="software_licenses",
        item_description="Error handling budget loader failure",
        quantity=1,
        unit_price=1000.0,
        total_amount=1000.0,
    )

    with patch("data.loader.load_budgets", side_effect=RuntimeError("budget backend unavailable")):
        recommendation = generate_recommendation(request)

    assert recommendation.decision in {"approve", "deny", "escalate"}
    assert recommendation.rationale.strip()
    assert "Budget check error" in recommendation.rationale
    assert "budget backend unavailable" in recommendation.rationale


def test_generate_recommendation_escalates_for_unknown_vendor() -> None:
    request = PurchaseRequest(
        request_id="REQ-ERR-002",
        requestor="Test User",
        cost_center_id="CC-001",
        vendor_name="Unknown Vendor",
        vendor_id="V-999",
        category="professional_services",
        item_description="Unknown vendor handling",
        quantity=1,
        unit_price=5000.0,
        total_amount=5000.0,
    )

    recommendation = generate_recommendation(request)

    assert recommendation.decision == "escalate"
    assert recommendation.rationale.strip()
    assert "Unknown vendor_id" in recommendation.rationale
