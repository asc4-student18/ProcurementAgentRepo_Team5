from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest
from tools.assess_risk import assess_risk
from tools.budget import check_budget
from tools.check_policy_compliance import check_policy_compliance
from tools.check_vendor_duplication import check_vendor_duplication


load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


DEFAULT_MODEL = os.getenv("PROCUREMENT_AGENT_MODEL", "openai-chat:gpt-4o-mini")
DIRECTOR_APPROVAL_THRESHOLD = 50000.0
NEAR_THRESHOLD_RATIO = 0.05

SYSTEM_PROMPT = (
    "You are a FedEx procurement intelligence assistant. "
    "For each valid purchase request, ensure budget, vendor duplication, policy compliance, "
    "and risk findings are included. "
    "If the request amount is within 5% of the director approval threshold, escalate. "
    "If any tool returns escalate, the final decision is always escalate. "
    "If no escalation signals exist and any tool returns deny, the final decision is deny. "
    "Approve only when no escalate or deny signals exist. "
    "If any tool returns an error payload, explicitly reference that error in rationale and escalate. "
    "Interpret boolean fields strictly: compliance_flag=False means no compliance hold and is not "
    "an escalation signal. "
    "If within_budget=True, deny_triggered=False, there are no policy violations, and risk_level is "
    "not critical, the final decision must be approve. "
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
    "Always return structured output conforming to ProcurementRecommendation with a non-empty rationale "
    "that references policy IDs and tool failures when applicable."
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
            rationale_points.append(
                "Budget check: "
                f"within_budget={budget_result['within_budget']}, "
                f"remaining_budget={budget_result['remaining_budget']}, "
                f"overage={budget_result['overage']}"
            )
            if not bool(budget_result["within_budget"]):
                deny_signals.append("budget overage")
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

    return ProcurementRecommendation(decision=decision, rationale=rationale)
