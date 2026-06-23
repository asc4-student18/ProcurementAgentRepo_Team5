# Proposal MD Issue and Fix Log: add-procurement-intelligence-agent

## Scope
This log records what issue existed in the proposal artifact and what update was made to fix it.

## 1. Risks were not explicitly documented in the proposal
Issue with existing artifact:
- The proposal scope and problem statement were clear, but risk coverage was only implicit and not explicitly listed.

Why this was a problem:
- Ambiguous risk visibility can cause missed mitigation planning during Sessions 2 and 3.

Update made to fix:
- Added an explicit `Key risks` section in the Impact block, including:
  - policy-conflict edge cases (overlapping escalate and deny signals)
  - conservative fallback behavior potentially increasing escalations
  - total amount consistency ambiguity (`total_amount` vs `quantity * unit_price`)

Updated file:
- openspec/changes/add-procurement-intelligence-agent/proposal.md

## 2. Capstone boundaries were not explicitly stated
Issue with existing artifact:
- The proposal did not explicitly declare out-of-scope boundaries, even though the requested scope was capstone-limited.

Why this was a problem:
- Without explicit boundaries, implementation may drift into non-capstone areas.

Update made to fix:
- Added an explicit `Out of scope for this capstone` list in the Impact block:
  - deployment/infrastructure changes
  - UI or frontend workflows
  - authentication/authorization features
  - persistent storage/database integrations

Updated file:
- openspec/changes/add-procurement-intelligence-agent/proposal.md

## 3. Existing strengths retained
Issue with existing artifact:
- No issue in core intent clarity.

Why this matters:
- The proposal already correctly matched the intended procurement-agent scope.

Update made:
- Retained existing sections and intent while applying only targeted risk/scope clarifications.

Updated file:
- openspec/changes/add-procurement-intelligence-agent/proposal.md

## Validation
- Command run: openspec validate add-procurement-intelligence-agent
- Result: Change is valid
