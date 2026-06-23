## ADDED Requirements

### Requirement: Policy compliance tool SHALL evaluate all eight procurement policies
The system SHALL provide a tool named `check_policy_compliance`.
Input contract: the tool MUST accept a purchase request payload containing at minimum `vendor_id`, `category`, `cost_center_id`, `quantity`, and `total_amount`.
Return contract: the tool MUST return `violations` and `evaluated_policy_ids` where `evaluated_policy_ids` includes `POL-001` through `POL-008`.

#### Scenario: All policies are evaluated
- **WHEN** a valid purchase request is provided
- **THEN** the tool SHALL evaluate exactly `POL-001`, `POL-002`, `POL-003`, `POL-004`, `POL-005`, `POL-006`, `POL-007`, and `POL-008`

### Requirement: Each violation SHALL include policy ID, violated rule, and forced decision
Each violation entry MUST include `policy_id`, `rule_violated`, and `forced_decision`.
The `forced_decision` MUST be one of `deny` or `escalate`.

#### Scenario: Violations are returned with required shape
- **WHEN** one or more policies are violated
- **THEN** each violation SHALL include `policy_id`, `rule_violated`, and `forced_decision`

#### Scenario: Prohibited-category policy violation
- **WHEN** request category is `catering`
- **THEN** the tool SHALL include a `POL-004` violation with `forced_decision=deny`

#### Scenario: Compliance-flagged vendor hold
- **WHEN** vendor is compliance-flagged
- **THEN** the tool SHALL include a `POL-006` violation with `forced_decision=escalate`

#### Scenario: Budget overage violation
- **WHEN** request total exceeds cost-center remaining budget
- **THEN** the tool SHALL include a `POL-008` violation with `forced_decision=deny`
