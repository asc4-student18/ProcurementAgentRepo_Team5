from __future__ import annotations

from agent import generate_recommendation
from data.loader import load_requests
from models import PurchaseRequest


def _get_request_by_id(request_id: str) -> PurchaseRequest:
    requests = load_requests()
    request = next(request for request in requests if request["request_id"] == request_id)
    return PurchaseRequest.model_validate(request)


def test_agent_approve_req_001() -> None:
    request = _get_request_by_id("REQ-001")

    result = generate_recommendation(request)

    assert result.decision == "approve"
    assert isinstance(result.rationale, str)
    assert result.rationale.strip()


def test_agent_deny_req_006_budget_overage() -> None:
    request = _get_request_by_id("REQ-006")

    result = generate_recommendation(request)

    assert result.decision == "deny"
    assert isinstance(result.rationale, str)
    assert result.rationale.strip()


def test_agent_policy_deny_req_009_catering_prohibition() -> None:
    request = _get_request_by_id("REQ-009")

    result = generate_recommendation(request)

    assert result.decision == "deny"
    assert isinstance(result.rationale, str)
    assert result.rationale.strip()


def test_agent_escalate_req_011_compliance_flagged_vendor() -> None:
    request = _get_request_by_id("REQ-011")

    result = generate_recommendation(request)

    assert result.decision == "escalate"
    assert isinstance(result.rationale, str)
    assert result.rationale.strip()
