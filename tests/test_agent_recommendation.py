import asyncio
import os
import re

import pytest

import agent
import data.loader
from agent import create_procurement_agent, generate_recommendation


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


def test_generate_recommendation_escalates_when_budget_check_raises(monkeypatch) -> None:
    def _raise_budget_error(cost_center_id: str, requested_amount: float) -> dict:
        raise RuntimeError("budget service unavailable")

    monkeypatch.setattr(agent, "check_budget", _raise_budget_error)

    request = {
        "request_id": "REQ-AGT-004",
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

    assert recommendation.decision == "escalate"
    assert "Budget check error: budget service unavailable" in recommendation.rationale
    assert "Escalation triggered by: Budget check failed" in recommendation.rationale


def test_generate_recommendation_rationale_includes_all_four_checks() -> None:
    request = {
        "request_id": "REQ-AGT-005",
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

    assert "Budget check:" in recommendation.rationale
    assert "Vendor check:" in recommendation.rationale
    assert "Policy check:" in recommendation.rationale
    assert "Risk check:" in recommendation.rationale


def test_generate_recommendation_escalates_when_budget_data_file_missing(
    monkeypatch,
) -> None:
    def _raise_file_missing() -> list[dict[str, object]]:
        raise FileNotFoundError("budgets.json missing")

    monkeypatch.setattr(data.loader, "load_budgets", _raise_file_missing)

    request = {
        "request_id": "REQ-AGT-006",
        "requestor": "Test User",
        "cost_center_id": "CC-001",
        "vendor_name": "Office Source Co",
        "vendor_id": "V-002",
        "category": "office_supplies",
        "item_description": "Office supplies restock",
        "quantity": 1,
        "unit_price": 1250.0,
        "total_amount": 1250.0,
        "manager_approved": True,
        "director_approved": False,
    }

    recommendation = generate_recommendation(request)

    assert recommendation.decision == "escalate"
    assert recommendation.rationale
    assert "Data loading failure" in recommendation.rationale
    assert "Budget check error" in recommendation.rationale


def test_system_prompt_includes_rationale_template_requirements() -> None:
    prompt = agent.SYSTEM_PROMPT

    assert "Rationale template requirements" in prompt
    assert "2 to 4 complete sentences" in prompt
    assert "no bullet points" in prompt
    assert "name the specific check or checks" in prompt
    assert "relevant amounts, vendor names, or policy IDs" in prompt


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_AGENT_TESTS") != "1",
    reason="Set RUN_LIVE_AGENT_TESTS=1 to enable live model formatting test.",
)
def test_live_agent_rationale_template_req_009() -> None:
    req = next(r for r in data.loader.load_requests() if r["request_id"] == "REQ-009")
    test_agent = create_procurement_agent()
    prompt = (
        "Evaluate this purchase request and return a ProcurementRecommendation: "
        f"{req}"
    )

    result = asyncio.run(test_agent.run(prompt))
    recommendation = result.output
    rationale = recommendation.rationale.strip()

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", rationale) if s.strip()]

    assert recommendation.decision == "deny"
    assert "POL-004" in rationale
    assert 2 <= len(sentences) <= 4
    assert all(re.search(r"[.!?]$", sentence) for sentence in sentences)
