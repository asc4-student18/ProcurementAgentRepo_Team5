from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest

from agent import generate_recommendation
from data.loader import load_requests
from models import PurchaseRequest


pytest.importorskip("pytest_asyncio")


def _get_request_by_id(request_id: str) -> PurchaseRequest:
    requests = load_requests()
    request = next(request for request in requests if request["request_id"] == request_id)
    return PurchaseRequest.model_validate(request)


async def _run_request(request: PurchaseRequest) -> SimpleNamespace:
    # Keep tests async while using deterministic tool-based recommendation logic.
    recommendation = await asyncio.to_thread(generate_recommendation, request)
    return SimpleNamespace(data=recommendation)


@pytest.mark.asyncio
async def test_agent_approve_req_001() -> None:
    request = _get_request_by_id("REQ-001")

    result = await _run_request(request)

    assert result.data.decision == "approve"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_deny_req_006_budget_overage() -> None:
    request = _get_request_by_id("REQ-006")

    result = await _run_request(request)

    assert result.data.decision == "deny"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_policy_deny_req_009_catering_prohibition() -> None:
    request = _get_request_by_id("REQ-009")

    result = await _run_request(request)

    assert result.data.decision == "deny"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_agent_escalate_req_011_compliance_flagged_vendor() -> None:
    request = _get_request_by_id("REQ-011")

    result = await _run_request(request)

    assert result.data.decision == "escalate"
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()
