from __future__ import annotations

from types import SimpleNamespace

import pytest

from agent import generate_recommendation
from data.loader import load_requests
from models import PurchaseRequest


def _get_request_by_id(request_id: str) -> PurchaseRequest:
    requests = load_requests()
    request = next(request for request in requests if request["request_id"] == request_id)
    return PurchaseRequest.model_validate(request)


def _get_request_record_by_id(request_id: str) -> dict[str, object]:
    requests = load_requests()
    return next(request for request in requests if request["request_id"] == request_id)


def _assert_valid_confidence(value: float) -> None:
    assert isinstance(value, float)
    assert 0.0 <= value <= 1.0


@pytest.mark.parametrize(
    "request_id",
    [
        "REQ-006",
        "REQ-007",
        "REQ-008",
        "REQ-009",
        "REQ-010",
        "REQ-011",
        "REQ-001",
        "REQ-002",
        "REQ-003",
    ],
)
def test_agent_decision_matches_expected_outcome_for_sample_requests(
    request_id: str,
) -> None:
    request_record = _get_request_record_by_id(request_id)
    request_model = PurchaseRequest.model_validate(request_record)

    result = SimpleNamespace(data=generate_recommendation(request_model))

    assert request_record["expected_outcome"] == result.data.decision
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()
    _assert_valid_confidence(result.data.confidence_score)


def test_agent_approve_req_001() -> None:
    request = _get_request_by_id("REQ-001")

    result = generate_recommendation(request)

    assert result.decision == "approve"
    assert isinstance(result.rationale, str)
    assert result.rationale.strip()
    _assert_valid_confidence(result.confidence_score)


def test_agent_deny_req_006_budget_overage() -> None:
    request = _get_request_by_id("REQ-006")

    result = generate_recommendation(request)

    assert result.decision == "deny"
    assert isinstance(result.rationale, str)
    assert result.rationale.strip()
    _assert_valid_confidence(result.confidence_score)


def test_agent_policy_deny_req_009_catering_prohibition() -> None:
    request = _get_request_by_id("REQ-009")

    result = generate_recommendation(request)

    assert result.decision == "deny"
    assert isinstance(result.rationale, str)
    assert result.rationale.strip()
    _assert_valid_confidence(result.confidence_score)


def test_agent_escalate_req_011_compliance_flagged_vendor() -> None:
    request = _get_request_by_id("REQ-011")

    result = generate_recommendation(request)

    assert result.decision == "escalate"
    assert isinstance(result.rationale, str)
    assert result.rationale.strip()
    _assert_valid_confidence(result.confidence_score)
