from agent import generate_recommendation


def test_generate_recommendation_escalate_precedence_over_deny() -> None:
    request = {
        "request_id": "REQ-AGT-001",
        "requestor": "Test User",
        "cost_center_id": "CC-004",
        "vendor_name": "NovaPrint Solutions",
        "vendor_id": "V-012",
        "category": "office_supplies",
        "item_description": "Bulk office supplies",
        "quantity": 1,
        "unit_price": 28500.0,
        "total_amount": 28500.0,
        "manager_approved": False,
        "director_approved": False,
    }

    recommendation = generate_recommendation(request)

    assert recommendation.decision == "escalate"
    assert recommendation.rationale
    assert "Risk check:" in recommendation.rationale


def test_generate_recommendation_deny_when_deny_signals_only() -> None:
    request = {
        "request_id": "REQ-AGT-002",
        "requestor": "Test User",
        "cost_center_id": "CC-010",
        "vendor_name": "Crestview Print and Media",
        "vendor_id": "V-010",
        "category": "marketing_materials",
        "item_description": "Print media",
        "quantity": 1,
        "unit_price": 5400.0,
        "total_amount": 5400.0,
        "manager_approved": True,
        "director_approved": False,
    }

    recommendation = generate_recommendation(request)

    assert recommendation.decision == "deny"
    assert "POL-005" in recommendation.rationale
    assert "Risk check:" in recommendation.rationale


def test_generate_recommendation_approve_when_no_blocking_findings() -> None:
    request = {
        "request_id": "REQ-AGT-003",
        "requestor": "Test User",
        "cost_center_id": "CC-005",
        "vendor_name": "FastTrack Couriers",
        "vendor_id": "V-004",
        "category": "courier_services",
        "item_description": "Courier service",
        "quantity": 1,
        "unit_price": 1200.0,
        "total_amount": 1200.0,
        "manager_approved": True,
        "director_approved": False,
    }

    recommendation = generate_recommendation(request)

    assert recommendation.decision == "approve"
    assert "no blocking findings" in recommendation.rationale.lower()
    assert "Risk check:" in recommendation.rationale
