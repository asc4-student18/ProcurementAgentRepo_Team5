## 1. Models and Contracts

- [ ] 1.1 Create `PurchaseRequest` and `ProcurementRecommendation` models in `models.py` with full type hints and decision literal constraints
- [ ] 1.2 Add model validators to enforce non-empty rationale and reject invalid or incomplete request payloads
- [ ] 1.3 Add tests covering valid model construction and invalid input/output rejection paths

## 2. Data Loader Foundation

- [ ] 2.1 Implement loader functions in `data/loader.py` for budgets, vendors, policies, and requests datasets
- [ ] 2.2 Add loader-level error handling for missing/invalid data files with deterministic structured error responses
- [ ] 2.3 Add tests verifying loader outputs and ensuring tool code can consume loader-returned structures

## 3. Procurement Evaluation Tools

- [ ] 3.1 Implement `check_budget` in `tools/` returning `within_budget`, `remaining_budget`, and `overage` plus structured errors for unknown cost centers
- [ ] 3.2 Implement `check_vendor_duplication` in `tools/` to detect active-contract conflicts and single-source restriction conditions
- [ ] 3.3 Implement `check_policy_compliance` in `tools/` to evaluate all policies and emit structured violations with policy IDs and forced decision effects
- [ ] 3.4 Implement `assess_risk` in `tools/` to return `compliance_flag`, `contract_status`, and computed `risk_level`
- [ ] 3.5 Add tests for `check_budget` primary success path and unknown-cost-center failure path
- [ ] 3.6 Add tests for `check_vendor_duplication` primary success path and vendor-lookup/data failure path
- [ ] 3.7 Add tests for `check_policy_compliance` primary success path and policy-data unavailability failure path
- [ ] 3.8 Add tests for `assess_risk` primary success path and vendor-metadata failure path

## 4. Agent Orchestration and Decision Logic

- [ ] 4.1 Implement `agent.py` using `pydantic-ai` with `output_type=ProcurementRecommendation`
- [ ] 4.2 Wire the four tools into recommendation flow and aggregate findings into normalized decision signals
- [ ] 4.3 Implement deterministic priority resolver `escalate > deny > approve` for combined signals
- [ ] 4.4 Ensure tool exceptions are caught and reflected in rationale with conservative escalation handling when needed

## 5. End-to-End Validation

- [ ] 5.1 Add integration tests covering at minimum one `approve`, one `deny`, one policy-driven deny, and one `escalate` sample request
- [ ] 5.2 Add edge-case tests for contradictory findings (escalate + deny), ambiguous inputs, and total amount consistency checks
- [ ] 5.3 Verify all 15 sample requests run end-to-end without unhandled exceptions

## 6. Compliance and Readiness

- [ ] 6.1 Run `openspec validate add-procurement-intelligence-agent` and resolve any structural issues
- [ ] 6.2 Run `pytest tests/ -v --tb=short --junitxml=docs/test-results.xml` and review failures
- [ ] 6.3 Update `docs/test-results.xml` and readiness documentation to support review and go/no-go evidence