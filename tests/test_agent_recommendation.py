import agent
import data.loader
from agent import (
    draft_requestor_reply_email,
    generate_recommendation,
    generate_recommendation_and_email,
    generate_recommendation_with_streaming,
    stream_recommendation_rationale,
)
from models import ProcurementRecommendation, RequestorEmailDraft


def _assert_valid_confidence(value: float) -> None:
    assert isinstance(value, float)
    assert 0.0 <= value <= 1.0


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
    _assert_valid_confidence(recommendation.confidence_score)


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
    _assert_valid_confidence(recommendation.confidence_score)


def test_generate_recommendation_approve_when_no_blocking_findings() -> None:
    request = {
        "request_id": "REQ-AGT-003",
        "requestor": "Test User",
        "cost_center_id": "CC-001",
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
    _assert_valid_confidence(recommendation.confidence_score)


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
    assert recommendation.confidence_score <= 0.6


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
    _assert_valid_confidence(recommendation.confidence_score)


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
    assert recommendation.confidence_score <= 0.6


def test_system_prompt_includes_rationale_template_requirements() -> None:
    prompt = agent.SYSTEM_PROMPT

    assert "Rationale template requirements" in prompt
    assert "exactly 4 complete sentences" in prompt
    assert "no bullet points" in prompt
    assert "Driving checks" in prompt
    assert "relevant amounts, vendor names, and policy IDs" in prompt
    assert "include confidence_score as a float between 0.0 and 1.0 inclusive" in prompt


def test_generate_recommendation_req_009_policy_deny() -> None:
    req = next(r for r in data.loader.load_requests() if r["request_id"] == "REQ-009")

    recommendation = generate_recommendation(req)
    rationale = recommendation.rationale.strip()

    assert recommendation.decision == "deny"
    assert "POL-004" in rationale
    _assert_valid_confidence(recommendation.confidence_score)


def test_generate_recommendation_req_009_has_high_confidence() -> None:
    req = next(r for r in data.loader.load_requests() if r["request_id"] == "REQ-009")

    recommendation = generate_recommendation(req)

    assert recommendation.decision == "deny"
    assert recommendation.confidence_score >= 0.9


def test_generate_recommendation_req_015_escalates_for_tight_budget() -> None:
    req = next(r for r in data.loader.load_requests() if r["request_id"] == "REQ-015")

    recommendation = generate_recommendation(req)
    rationale = recommendation.rationale.strip().lower()

    assert recommendation.decision == "escalate"
    assert "low remaining budget after purchase" in rationale
    _assert_valid_confidence(recommendation.confidence_score)


def test_draft_requestor_reply_email_uses_second_agent(monkeypatch) -> None:
    class FakeEmailAgent:
        def run_sync(self, prompt: str):
            assert "decision=deny" in prompt
            assert "rationale=Policy check violations: POL-004" in prompt

            class _Result:
                output = RequestorEmailDraft(
                    subject="Update on purchase request REQ-EMAIL-001",
                    body="Your request was denied due to policy restrictions.",
                )

            return _Result()

    monkeypatch.setattr(agent, "create_email_drafter_agent", lambda model=None: FakeEmailAgent())

    request = {
        "request_id": "REQ-EMAIL-001",
        "requestor": "Test User",
        "cost_center_id": "CC-001",
        "vendor_name": "Office Source Co",
        "vendor_id": "V-002",
        "category": "office_supplies",
        "item_description": "Paper",
        "quantity": 1,
        "unit_price": 100.0,
        "total_amount": 100.0,
    }
    recommendation = ProcurementRecommendation(
        decision="deny",
        rationale="Policy check violations: POL-004",
        confidence_score=0.95,
    )

    email = draft_requestor_reply_email(
        request=agent.PurchaseRequest.model_validate(request),
        recommendation=recommendation,
    )

    assert email.subject
    assert email.body


def test_generate_recommendation_and_email_chains_in_sequence(monkeypatch) -> None:
    call_order: list[str] = []

    def _fake_generate_recommendation(
        purchase_request: agent.PurchaseRequest | dict[str, object],
    ) -> ProcurementRecommendation:
        call_order.append("recommendation")
        assert isinstance(purchase_request, agent.PurchaseRequest)
        return ProcurementRecommendation(
            decision="approve",
            rationale="All checks passed",
            confidence_score=0.85,
        )

    def _fake_draft_requestor_reply_email(
        request: agent.PurchaseRequest,
        recommendation: ProcurementRecommendation,
        model: str | None = None,
    ) -> RequestorEmailDraft:
        call_order.append("email")
        assert request.request_id == "REQ-CHAIN-001"
        assert recommendation.decision == "approve"
        assert model == "openai-chat:gpt-4o-mini"
        return RequestorEmailDraft(
            subject="Update on your request REQ-CHAIN-001",
            body="Your request has been approved.",
        )

    monkeypatch.setattr(agent, "generate_recommendation", _fake_generate_recommendation)
    monkeypatch.setattr(agent, "draft_requestor_reply_email", _fake_draft_requestor_reply_email)

    request = {
        "request_id": "REQ-CHAIN-001",
        "requestor": "Jordan Lee",
        "cost_center_id": "CC-001",
        "vendor_name": "Office Source Co",
        "vendor_id": "V-002",
        "category": "office_supplies",
        "item_description": "Printer toner",
        "quantity": 1,
        "unit_price": 150.0,
        "total_amount": 150.0,
    }

    recommendation, email = generate_recommendation_and_email(
        request,
        email_model="openai-chat:gpt-4o-mini",
    )

    assert recommendation.decision == "approve"
    assert email.subject
    assert call_order == ["recommendation", "email"]


def test_generate_recommendation_with_streaming_returns_chunks_and_output(monkeypatch) -> None:
    class FakeStreamResult:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def stream_text(self, delta: bool = False, debounce_by: float | None = 0.1):
            assert delta is True
            assert debounce_by == 0.05
            yield "Decision: deny"
            yield " due to POL-004"

        def get_output(self):
            return ProcurementRecommendation(
                decision="deny",
                rationale="Decision: deny due to POL-004",
                confidence_score=0.95,
            )

    class FakeStreamingAgent:
        def run_stream_sync(self, prompt: str):
            assert '"request_id": "REQ-STREAM-001"' in prompt
            return FakeStreamResult()

    monkeypatch.setattr(agent, "create_procurement_agent", lambda model=None: FakeStreamingAgent())

    collected_chunks: list[str] = []
    request = {
        "request_id": "REQ-STREAM-001",
        "requestor": "Taylor",
        "cost_center_id": "CC-001",
        "vendor_name": "Office Source Co",
        "vendor_id": "V-002",
        "category": "office_supplies",
        "item_description": "Paper",
        "quantity": 1,
        "unit_price": 100.0,
        "total_amount": 100.0,
    }

    recommendation, chunks = generate_recommendation_with_streaming(
        request,
        on_rationale_chunk=collected_chunks.append,
    )

    assert recommendation.decision == "deny"
    assert chunks == ["Decision: deny", " due to POL-004"]
    assert collected_chunks == chunks


def test_stream_recommendation_rationale_yields_incremental_chunks(monkeypatch) -> None:
    class FakeStreamResult:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def stream_text(self, delta: bool = False, debounce_by: float | None = 0.1):
            assert delta is True
            assert debounce_by == 0.05
            yield "chunk-1"
            yield "chunk-2"

    class FakeStreamingAgent:
        def run_stream_sync(self, prompt: str):
            assert '"request_id": "REQ-STREAM-002"' in prompt
            return FakeStreamResult()

    monkeypatch.setattr(agent, "create_procurement_agent", lambda model=None: FakeStreamingAgent())

    request = {
        "request_id": "REQ-STREAM-002",
        "requestor": "Avery",
        "cost_center_id": "CC-001",
        "vendor_name": "Office Source Co",
        "vendor_id": "V-002",
        "category": "office_supplies",
        "item_description": "Pens",
        "quantity": 1,
        "unit_price": 50.0,
        "total_amount": 50.0,
    }

    chunks = list(stream_recommendation_rationale(request))

    assert chunks == ["chunk-1", "chunk-2"]
