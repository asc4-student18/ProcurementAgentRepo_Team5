## Context

The project currently has mock procurement datasets and acceptance criteria but no implemented procurement intelligence workflow. The change introduces a Pydantic AI based advisory agent that pre-screens requests and emits structured recommendations for procurement officers.

Key constraints:
- Python 3.11+ with Pydantic v2 models and `pydantic-ai` agent construction.
- Agent output must always conform to a typed `ProcurementRecommendation` schema with decision constrained to `approve`, `deny`, or `escalate`.
- Tool code and tests MUST load reference data via `data/loader.py`; direct reads from `mock_data/` are disallowed.
- Tool failures must not crash recommendation generation; failures must be reflected in rationale text.

Primary stakeholders:
- Procurement officers (final decision-makers)
- Procurement managers/directors (approval governance)
- Legal/compliance reviewers (flagged vendor flow)

## Goals / Non-Goals

**Goals:**
- Provide deterministic pre-screening across four checks: budget, vendor duplication, policy compliance, and risk.
- Enforce validation on both agent input and output with explicit refusal/escalation behavior for invalid or partial data.
- Standardize decision mapping using priority `escalate > deny > approve`.
- Preserve explainability by requiring rationale references to check outcomes and any tool failures.
- Achieve tool-level and integration-level test coverage for primary success paths and edge cases.

**Non-Goals:**
- Fully automating procurement approvals without human review.
- Replacing enterprise source systems or live vendor/budget backends.
- Building a user interface in this change.
- Redefining policy thresholds beyond what is encoded in the mock policy dataset.

## Decisions

1. **Decision: Typed domain boundary with Pydantic models**
   - Choice: Introduce strict `PurchaseRequest` and `ProcurementRecommendation` models.
   - Rationale: Enforces reliable schema contracts and prevents free-form outputs.
   - Alternative considered: Untyped dict payloads.
   - Why not alternative: weak guarantees and harder-to-test output correctness.

2. **Decision: Single data access abstraction via `data/loader.py`**
   - Choice: All tools and tests call loader functions for budgets/vendors/policies/requests.
   - Rationale: Centralized validation and easier test stubbing.
   - Alternative considered: each tool reading JSON files directly.
   - Why not alternative: duplicates parsing logic and violates project conventions.

3. **Decision: Four-tool evaluation architecture in `tools/`**
   - Choice: Keep each check in an isolated tool (`check_budget`, `check_vendor_duplication`, `check_policy_compliance`, `assess_risk`).
   - Rationale: Improves composability, observability, and targeted testing.
   - Alternative considered: monolithic evaluation function.
   - Why not alternative: reduced clarity and more brittle tests.

4. **Decision: Deterministic recommendation combiner with precedence `escalate > deny > approve`**
   - Choice: Aggregate tool findings into normalized signals, then resolve final decision by precedence.
   - Rationale: Handles mixed evidence predictably and supports conservative governance.
   - Alternative considered: deny-first precedence or score-based blending.
   - Why not alternative: deny-first conflicts with specified precedence; score-only approaches reduce interpretability.

5. **Decision: Failure-tolerant execution with explicit rationale disclosure**
   - Choice: Catch tool exceptions and include failure notes in rationale, defaulting to conservative escalation when confidence is reduced.
   - Rationale: Prevents silent failures and keeps procurement officer informed.
   - Alternative considered: hard failure on any tool error.
   - Why not alternative: breaks end-to-end processing requirements and reduces operational reliability.

## Risks / Trade-offs

- **[Risk] Policy interpretation conflicts in edge cases (e.g., budget overage with escalation cues)** -> **Mitigation:** encode precedence rules explicitly and add tests for contradictory combinations.
- **[Risk] Data inconsistency between provided `total_amount` and computed `quantity * unit_price`** -> **Mitigation:** validate and surface discrepancy in rationale/escalation path.
- **[Risk] Over-escalation due to conservative error handling** -> **Mitigation:** distinguish hard policy violations from uncertainty-induced escalations in rationale wording.
- **[Risk] Tool output drift can break combiner assumptions** -> **Mitigation:** define stable typed tool result structures and unit tests per tool contract.

## Migration Plan

- Step 1: Introduce models and data loader with unit tests.
- Step 2: Implement four tools with tool-level tests.
- Step 3: Wire agent orchestration with structured output contract (`output_type=ProcurementRecommendation`).
- Step 4: Add integration tests across representative request outcomes (approve/deny/escalate, partial-data, tool-failure).
- Step 5: Run full test suite and OpenSpec validation before implementation handoff.

Rollback approach:
- Revert change set files (`agent.py`, `models.py`, `data/loader.py`, `tools/`, `tests/`) to prior baseline; no external migrations are required because the change only adds local code paths.

## Open Questions

- Should data-validation anomalies (for example mismatched totals) always force `escalate`, or only when material variance crosses a threshold?
- For simultaneous hard-deny and mandatory-escalate findings, should rationale include both while still honoring `escalate > deny > approve` precedence?
- Should ambiguous samples be expected as deterministic test outcomes or as policy-tunable scenarios?