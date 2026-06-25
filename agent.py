from __future__ import annotations

import json
import os
from typing import Any, Callable, Iterator

from dotenv import load_dotenv
from pydantic_ai import Agent

from data import loader
from models import ProcurementRecommendation, PurchaseRequest, RequestorEmailDraft
from tools.assess_risk import assess_risk
from tools.budget import check_budget
from tools.check_policy_compliance import check_policy_compliance
from tools.check_vendor_duplication import check_vendor_duplication


load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


DEFAULT_MODEL = os.getenv("PROCUREMENT_AGENT_MODEL", "openai-chat:gpt-4o-mini")
EMAIL_DRAFTER_MODEL = os.getenv("PROCUREMENT_EMAIL_AGENT_MODEL", DEFAULT_MODEL)
DIRECTOR_APPROVAL_THRESHOLD = 50000.0
NEAR_THRESHOLD_RATIO = 0.05
TIGHT_BUDGET_POST_PURCHASE_RATIO = 0.20

SYSTEM_PROMPT = (
    "You are a FedEx procurement intelligence assistant. "
    "For each valid purchase request, ensure budget, vendor duplication, policy compliance, "
    "and risk findings are included. "
    "If the request amount is within 5% of the director approval threshold, escalate. "
    "If budget data indicates a tight-budget scenario where post_purchase_remaining = "
    "remaining_budget - requested_amount is less than 20% of quarterly_budget, escalate and "
    "explicitly flag the low remaining budget in rationale. "
    "If any tool returns escalate, the final decision is always escalate. "
    "If no escalation signals exist and any tool returns deny, the final decision is deny. "
    "Approve only when no escalate or deny signals exist. "
    "If any tool returns an error payload, explicitly reference that error in rationale and escalate. "
    "Interpret boolean fields strictly: compliance_flag=False means no compliance hold and is not "
    "an escalation signal. "
    "If within_budget=True, deny_triggered=False, there are no policy violations, risk_level is "
    "not critical, and the request is not a tight-budget scenario, the final decision must be approve. "
    "Rationale template requirements: write exactly 4 complete sentences with no bullet points. "
    "Use this exact structure for sentence 1 as a single sentence: 'Decision: <approve|deny|escalate>; "
    "Driving checks: <one or more exact labels>.' "
    "The only valid driving-check labels are exactly: Budget check, Vendor check, Policy check, Risk check, "
    "Amount check. "
    "Do not use lowercase variants or paraphrases like 'risk findings' or 'policy review'. "
    "Sentence 2 must include concrete supporting details such as relevant amounts, vendor names, "
    "and policy IDs when applicable. "
    "Sentence 3 and sentence 4 must summarize secondary checks or error handling while preserving the "
    "same decision. "
    "Always include confidence_score as a float between 0.0 and 1.0 inclusive using this rubric: "
    "1.0 when only one check fired and its outcome is unambiguous (for example, sole catering "
    "prohibition); 0.8 to 0.9 when two or more checks fired and all agree; 0.5 to 0.7 when checks "
    "fired but at least one is borderline (near a threshold); below 0.5 when the agent could not "
    "determine a clear decision, and in that case the final decision must be escalate. "
    "Always return structured output conforming to ProcurementRecommendation with a non-empty rationale "
    "that references policy IDs and tool failures when applicable."
)

EMAIL_DRAFTER_SYSTEM_PROMPT = (
    "You draft professional procurement-status emails to purchase requestors. "
    "Use the provided request details and recommendation. "
    "Keep tone clear, concise, and neutral. "
    "Do not invent policy IDs, vendor details, or monetary amounts not present in the input. "
    "For deny and escalate decisions, explicitly list the next action required by the requestor. "
    "Return structured output conforming to RequestorEmailDraft with a non-empty subject and body."
)


def _record_tool_exception(
    check_name: str,
    exc: Exception,
    rationale_points: list[str],
    escalate_signals: list[str],
) -> None:
    error_note = f"{check_name} failed"
    escalate_signals.append(error_note)
    rationale_points.append(f"{check_name} error: {exc}")


def _resolve_decision(escalate_signals: list[str], deny_signals: list[str]) -> str:
    if escalate_signals:
        return "escalate"
    if deny_signals:
        return "deny"
    return "approve"


def create_procurement_agent(model: str | None = None) -> Agent:
    selected_model = model or DEFAULT_MODEL
    return Agent(
        selected_model,
        output_type=ProcurementRecommendation,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            check_budget,
            check_vendor_duplication,
            check_policy_compliance,
            assess_risk,
        ],
    )


def generate_recommendation_with_streaming(
    purchase_request: PurchaseRequest | dict[str, Any],
    model: str | None = None,
    on_rationale_chunk: Callable[[str], None] | None = None,
    debounce_by: float | None = 0.05,
) -> tuple[ProcurementRecommendation, list[str]]:
    """Run the recommendation agent with streaming and return rationale chunks incrementally."""

    request = (
        purchase_request
        if isinstance(purchase_request, PurchaseRequest)
        else PurchaseRequest.model_validate(purchase_request)
    )
    prompt = json.dumps(request.model_dump(), ensure_ascii=True)
    streamed_result = create_procurement_agent(model=model).run_stream_sync(prompt)
    rationale_chunks: list[str] = []

    with streamed_result:
        for chunk in streamed_result.stream_text(delta=True, debounce_by=debounce_by):
            if not chunk:
                continue
            rationale_chunks.append(chunk)
            if on_rationale_chunk is not None:
                on_rationale_chunk(chunk)

        recommendation = streamed_result.get_output()

    return recommendation, rationale_chunks


def stream_recommendation_rationale(
    purchase_request: PurchaseRequest | dict[str, Any],
    model: str | None = None,
    debounce_by: float | None = 0.05,
) -> Iterator[str]:
    """Yield recommendation rationale chunks using the Pydantic AI streaming API."""

    request = (
        purchase_request
        if isinstance(purchase_request, PurchaseRequest)
        else PurchaseRequest.model_validate(purchase_request)
    )
    prompt = json.dumps(request.model_dump(), ensure_ascii=True)
    streamed_result = create_procurement_agent(model=model).run_stream_sync(prompt)

    with streamed_result:
        for chunk in streamed_result.stream_text(delta=True, debounce_by=debounce_by):
            if chunk:
                yield chunk


def create_email_drafter_agent(model: str | None = None) -> Agent:
    selected_model = model or EMAIL_DRAFTER_MODEL
    return Agent(
        selected_model,
        output_type=RequestorEmailDraft,
        system_prompt=EMAIL_DRAFTER_SYSTEM_PROMPT,
    )


def draft_requestor_reply_email(
    request: PurchaseRequest,
    recommendation: ProcurementRecommendation,
    model: str | None = None,
) -> RequestorEmailDraft:
    prompt = (
        "Draft an email to the purchase requestor using the recommendation below. "
        "Request details: "
        f"request_id={request.request_id}, requestor={request.requestor}, vendor={request.vendor_name}, "
        f"category={request.category}, total_amount={request.total_amount}. "
        "Recommendation details: "
        f"decision={recommendation.decision}, confidence_score={recommendation.confidence_score}, "
        f"rationale={recommendation.rationale}."
    )
    result = create_email_drafter_agent(model=model).run_sync(prompt)
    return result.output


def generate_recommendation_and_email(
    purchase_request: PurchaseRequest | dict[str, Any],
    email_model: str | None = None,
) -> tuple[ProcurementRecommendation, RequestorEmailDraft]:
    request = (
        purchase_request
        if isinstance(purchase_request, PurchaseRequest)
        else PurchaseRequest.model_validate(purchase_request)
    )
    recommendation = generate_recommendation(request)
    email_draft = draft_requestor_reply_email(
        request=request,
        recommendation=recommendation,
        model=email_model,
    )
    return recommendation, email_draft


def generate_recommendation(
    purchase_request: PurchaseRequest | dict[str, Any],
) -> ProcurementRecommendation:
    raw_request = purchase_request if isinstance(purchase_request, dict) else None
    request = (
        purchase_request
        if isinstance(purchase_request, PurchaseRequest)
        else PurchaseRequest.model_validate(purchase_request)
    )

    policy_input: dict[str, Any] = request.model_dump()
    if raw_request is not None:
        if "manager_approved" in raw_request:
            policy_input["manager_approved"] = raw_request["manager_approved"]
        if "director_approved" in raw_request:
            policy_input["director_approved"] = raw_request["director_approved"]

    rationale_points: list[str] = []
    deny_signals: list[str] = []
    escalate_signals: list[str] = []
    tight_budget_detected = False

    near_director_threshold_floor = DIRECTOR_APPROVAL_THRESHOLD * (1.0 - NEAR_THRESHOLD_RATIO)
    if near_director_threshold_floor <= request.total_amount < DIRECTOR_APPROVAL_THRESHOLD:
        escalate_signals.append("near director approval threshold")
        rationale_points.append(
            "Amount check: "
            f"total_amount={request.total_amount} is within 5% of director threshold "
            f"{DIRECTOR_APPROVAL_THRESHOLD}"
        )

    # Evaluate budget signals.
    try:
        budget_result = check_budget(
            cost_center_id=request.cost_center_id,
            requested_amount=request.total_amount,
        )
        budget_error = budget_result.get("error")
        if budget_error:
            escalate_signals.append("budget check failed")
            rationale_points.append(
                "Budget check error: "
                f"{budget_error.get('code', 'UNKNOWN_ERROR')} - "
                f"{budget_error.get('message', 'No error message provided')}"
            )
        else:
            remaining_budget = float(budget_result["remaining_budget"])
            rationale_points.append(
                "Budget check: "
                f"within_budget={budget_result['within_budget']}, "
                f"remaining_budget={budget_result['remaining_budget']}, "
                f"overage={budget_result['overage']}"
            )
            if not bool(budget_result["within_budget"]):
                deny_signals.append("budget overage")
            else:
                budgets = loader.load_budgets()
                budget_row = next(
                    (
                        item
                        for item in budgets
                        if str(item.get("cost_center_id", "")) == request.cost_center_id
                    ),
                    None,
                )
                if budget_row is not None:
                    quarterly_budget = float(budget_row.get("quarterly_budget", 0.0))
                    post_purchase_remaining = remaining_budget - request.total_amount
                    if (
                        quarterly_budget > 0
                        and post_purchase_remaining
                        < quarterly_budget * TIGHT_BUDGET_POST_PURCHASE_RATIO
                    ):
                        tight_budget_detected = True
                        rationale_points.append(
                            "Amount check: "
                            f"post_purchase_remaining={post_purchase_remaining} is below "
                            f"20% of quarterly_budget={quarterly_budget}"
                        )
    except Exception as exc:
        _record_tool_exception(
            check_name="Budget check",
            exc=exc,
            rationale_points=rationale_points,
            escalate_signals=escalate_signals,
        )

    # Evaluate vendor duplication signals.
    try:
        vendor_duplication = check_vendor_duplication(
            vendor_id=request.vendor_id,
            purchase_category=request.category,
            total_amount=request.total_amount,
        )
        vendor_error = vendor_duplication.get("error")
        if vendor_error:
            escalate_signals.append("vendor duplication check reported error")
            rationale_points.append(
                "Vendor check error: "
                f"{vendor_error.get('code', 'UNKNOWN_ERROR')} - "
                f"{vendor_error.get('message', 'No error message provided')}"
            )
        else:
            rationale_points.append(f"Vendor check: {vendor_duplication['message']}")
            if vendor_duplication["deny_triggered"]:
                deny_signals.append("POL-001 single-source restriction")
    except Exception as exc:
        _record_tool_exception(
            check_name="Vendor check",
            exc=exc,
            rationale_points=rationale_points,
            escalate_signals=escalate_signals,
        )

    # Evaluate policy violations and forced decisions.
    try:
        policy_result = check_policy_compliance(policy_input)
        policy_error = policy_result.get("error")
        if policy_error:
            escalate_signals.append("policy compliance check reported error")
            rationale_points.append(
                "Policy check error: "
                f"{policy_error.get('code', 'UNKNOWN_ERROR')} - "
                f"{policy_error.get('message', 'No error message provided')}"
            )
        else:
            if policy_result["violations"]:
                policies = ", ".join(v["policy_id"] for v in policy_result["violations"])
                rationale_points.append(f"Policy check violations: {policies}")
            else:
                rationale_points.append("Policy check: no violations")

            for violation in policy_result["violations"]:
                if violation["forced_decision"] == "escalate":
                    escalate_signals.append(f"{violation['policy_id']} policy escalation")
                elif violation["forced_decision"] == "deny":
                    deny_signals.append(f"{violation['policy_id']} policy denial")
    except Exception as exc:
        _record_tool_exception(
            check_name="Policy check",
            exc=exc,
            rationale_points=rationale_points,
            escalate_signals=escalate_signals,
        )

    # Evaluate vendor risk profile.
    try:
        risk_profile = assess_risk(request.vendor_id)
        risk_error = risk_profile.get("error")
        if risk_error:
            escalate_signals.append("risk assessment check reported error")
            rationale_points.append(
                "Risk check error: "
                f"{risk_error.get('code', 'UNKNOWN_ERROR')} - "
                f"{risk_error.get('message', 'No error message provided')}"
            )
        else:
            rationale_points.append(
                "Risk check: "
                f"level={risk_profile['risk_level']}, "
                f"contract_status={risk_profile['contract_status']}, "
                f"compliance_flag={risk_profile['compliance_flag']}"
            )
            if risk_profile["risk_level"] == "critical":
                escalate_signals.append("critical vendor risk profile")
    except Exception as exc:
        _record_tool_exception(
            check_name="Risk check",
            exc=exc,
            rationale_points=rationale_points,
            escalate_signals=escalate_signals,
        )

    if tight_budget_detected and not deny_signals:
        escalate_signals.append("low remaining budget after purchase")

    decision = _resolve_decision(escalate_signals=escalate_signals, deny_signals=deny_signals)

    if decision == "escalate":
        rationale_points.append(
            "Escalation triggered by: " + ", ".join(sorted(set(escalate_signals)))
        )
    elif decision == "deny":
        rationale_points.append("Denial triggered by: " + ", ".join(sorted(set(deny_signals))))
    else:
        rationale_points.append("All evaluated checks passed with no blocking findings")

    rationale = "; ".join(rationale_points).strip()
    if not rationale:
        rationale = "No explicit findings were produced; escalating for manual review."
        decision = "escalate"

    if decision == "approve":
        confidence_score = 0.85
    elif decision == "deny":
        confidence_score = 0.9
    else:
        confidence_score = 0.8

    if any("error" in point.lower() for point in rationale_points):
        confidence_score = min(confidence_score, 0.6)

    return ProcurementRecommendation(
        decision=decision,
        rationale=rationale,
        confidence_score=confidence_score,
    )
