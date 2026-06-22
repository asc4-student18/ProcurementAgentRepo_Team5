# User Stories: Procurement Intelligence Agent

These user stories define the scope of the capstone implementation.
Reference the applicable story ID in every commit message using the format:

```
[US-XXX] Short description of change
```

Example: `[US-001] Implement check_budget with overage detection`

---

| ID | Role | Need | Acceptance Signal |
|----|------|------|-------------------|
| US-001 | Procurement Officer | Screen purchase requests against cost center budget limits before approval | `check_budget` returns `within_budget`, `remaining_budget`, and `overage` for any valid cost center ID; unknown cost centers return a structured error |
| US-002 | Procurement Officer | Detect when a requested vendor duplicates an existing active contract in the same category | `check_vendor_duplication` identifies conflicting active vendor IDs and applies the POL-001 $25,000 amount threshold |
| US-003 | Procurement Officer | Evaluate requests against all procurement policies before a recommendation is issued | `check_policy_compliance` returns violations with `policy_id`, rule description, and forced decision for all eight policies in `mock_data/policies.json` |
| US-004 | Procurement Manager | Flag vendors with compliance issues or expired contracts for additional scrutiny | `assess_risk` returns `compliance_flag`, `contract_status`, and a computed `risk_level` (`low` / `medium` / `high` / `critical`) for any vendor ID |
| US-005 | Procurement Officer | Receive a structured recommendation (approve, deny, or escalate) with written rationale for every request | `ProcurementRecommendation.rationale` is non-empty and references specific findings; `decision` is always one of the three allowed values |

---

## Story-to-Session Mapping

| Session | Primary Stories |
|---------|----------------|
| Session 1 | All (specification phase: all stories are scoped in the spec) |
| Session 2 | US-001 (budget tool), US-005 (models and agent shell) |
| Session 3 | US-002, US-003, US-004 (remaining tools), US-005 (full agent integration) |
| Session 4 | US-005 (test coverage and peer review) |
| Session 5 | US-005 (final verify and showcase) |

---

*These stories map to the acceptance criteria in `README.md`.*
*A single commit may reference multiple story IDs if the change spans more than one:*
*`[US-001][US-005] Add budget overage to recommendation rationale`*
