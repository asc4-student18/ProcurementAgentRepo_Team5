## Why

FedEx procurement analysts spend significant time manually triaging routine purchase requests that follow repeatable policy and budget patterns. A structured procurement intelligence agent is needed now to consistently pre-screen high-volume requests, reduce analyst workload, and provide explainable recommendations while preserving human final decision authority.

## What Changes

- Introduce a Procurement Intelligence Agent that accepts a purchase request and returns a structured recommendation constrained to `approve`, `deny`, or `escalate` with a non-empty rationale.
- Add Pydantic v2 domain models for request and recommendation validation, including strict output decision constraints.
- Add a central mock data loader in `data/loader.py` as the only supported data access path for tools and tests.
- Implement four procurement checks as agent-callable tools:
  - budget validation against cost-center remaining budget
  - vendor duplication and contract alignment detection
  - policy compliance evaluation across defined policies
  - vendor risk assessment using contract/compliance signals
- Define deterministic decision-priority behavior (`escalate > deny > approve`) and require tool failures to be surfaced in rationale instead of causing crashes.
- Add tests for tool success paths, key decision outcomes, and partial-data/tool-error scenarios.

## Capabilities

### New Capabilities
- `procurement-models`: Define validated Pydantic input/output schemas for procurement requests and recommendations.
- `procurement-data-loader`: Provide a single loader interface for mock procurement datasets used by tools and tests.
- `procurement-evaluation-tools`: Implement the four procurement evaluation tools and their structured outputs/error signaling.
- `procurement-recommendation-agent`: Orchestrate tools in a Pydantic AI agent and map findings to `approve`/`deny`/`escalate` recommendations with rationale.

### Modified Capabilities
- None.

## Impact

- Affected code: `agent.py`, `models.py`, `data/loader.py`, `tools/`, and `tests/`.
- Affected behavior: adds end-to-end procurement pre-screen recommendation flow over sample requests.
- Dependencies/constraints: Pydantic AI agent output must use typed structured output; no direct reads from `mock_data/` in tool code.
- Delivery impact: enables policy-consistent triage while keeping procurement officers as final approvers.
- Key risks:
  - Policy-conflict edge cases (for example overlapping escalate and deny signals) may create ambiguous decision expectations without strict precedence tests.
  - Tool/data lookup failures may increase escalation volume if fallback behavior is too conservative.
  - Input amount inconsistencies (`total_amount` vs `quantity * unit_price`) may produce avoidable escalations or rejections if tolerance rules are not explicit.
- Out of scope for this capstone:
  - Deployment/infrastructure changes.
  - UI or frontend workflows.
  - Authentication/authorization features.
  - Persistent storage/database integrations.
