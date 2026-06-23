from __future__ import annotations

import os

from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest
from tools.assess_risk import assess_risk
from tools.check_policy_compliance import check_policy_compliance
from tools.check_vendor_duplication import check_vendor_duplication


DEFAULT_MODEL = os.getenv("PROCUREMENT_AGENT_MODEL", "anthropic:claude-3-5-haiku-latest")


def create_procurement_agent(model: str | None = None) -> Agent:
    selected_model = model or DEFAULT_MODEL
    return Agent(
        selected_model,
        output_type=ProcurementRecommendation,
        system_prompt=(
            "You are a FedEx procurement intelligence assistant. "
            "Return only structured procurement recommendations."
        ),
    )


def generate_recommendation(purchase_request: PurchaseRequest | dict) -> ProcurementRecommendation:
    request = (
        purchase_request
        if isinstance(purchase_request, PurchaseRequest)
        else PurchaseRequest.model_validate(purchase_request)
    )

    rationale_points: list[str] = []
    deny_signals: list[str] = []
    escalate_signals: list[str] = []

    # Evaluate vendor duplication signals.
    try:
        vendor_duplication = check_vendor_duplication(
            vendor_id=request.vendor_id,
            purchase_category=request.category,
            total_amount=request.total_amount,
        )
        rationale_points.append(f"Vendor check: {vendor_duplication['message']}")
        if vendor_duplication["deny_triggered"]:
            deny_signals.append("POL-001 single-source restriction")
    except Exception as exc:
        escalate_signals.append("vendor duplication check failed")
        rationale_points.append(f"Vendor check error: {exc}")

    # Evaluate policy violations and forced decisions.
    try:
        policy_result = check_policy_compliance(request.model_dump())
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
        escalate_signals.append("policy compliance check failed")
        rationale_points.append(f"Policy check error: {exc}")

    # Evaluate vendor risk profile.
    try:
        risk_profile = assess_risk(request.vendor_id)
        rationale_points.append(
            "Risk check: "
            f"level={risk_profile['risk_level']}, "
            f"contract_status={risk_profile['contract_status']}, "
            f"compliance_flag={risk_profile['compliance_flag']}"
        )
        if risk_profile["risk_level"] == "critical":
            escalate_signals.append("critical vendor risk profile")
    except Exception as exc:
        escalate_signals.append("risk assessment check failed")
        rationale_points.append(f"Risk check error: {exc}")

    if escalate_signals:
        decision = "escalate"
        rationale_points.append(
            "Escalation triggered by: " + ", ".join(sorted(set(escalate_signals)))
        )
    elif deny_signals:
        decision = "deny"
        rationale_points.append("Denial triggered by: " + ", ".join(sorted(set(deny_signals))))
    else:
        decision = "approve"
        rationale_points.append("All evaluated checks passed with no blocking findings")

    return ProcurementRecommendation(decision=decision, rationale="; ".join(rationale_points))
