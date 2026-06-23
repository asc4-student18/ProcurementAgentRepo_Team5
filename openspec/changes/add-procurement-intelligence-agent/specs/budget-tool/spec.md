## ADDED Requirements

### Requirement: Budget check tool SHALL report spend feasibility
The system SHALL provide a tool named `check_budget`.
Input contract: the tool MUST accept `cost_center_id` and `total_amount` from a purchase request context.
Return contract: the tool MUST return `within_budget`, `remaining_budget`, and `overage`.

#### Scenario: Request is within remaining budget
- **WHEN** `total_amount` is less than or equal to the cost center's `remaining` budget
- **THEN** `within_budget` SHALL be `true`, `remaining_budget` SHALL reflect the matched cost center balance, and `overage` SHALL be `0`

#### Scenario: Request exceeds remaining budget
- **WHEN** `total_amount` is greater than the cost center's `remaining` budget
- **THEN** `within_budget` SHALL be `false`, `remaining_budget` SHALL reflect the matched cost center balance, and `overage` SHALL be a positive value

#### Scenario: Request exactly equals remaining budget
- **WHEN** `total_amount` equals the cost center's `remaining` budget
- **THEN** `within_budget` SHALL be `true` and `overage` SHALL be `0`

### Requirement: Budget check SHALL support policy-driven denial evaluation for overage
The budget result MUST be sufficient for policy evaluation against POL-008 (Budget Overage Prohibition).

#### Scenario: Overage supports POL-008 evaluation
- **WHEN** `within_budget` is `false`
- **THEN** the returned `overage` and `remaining_budget` SHALL provide enough context for a downstream `POL-008` deny decision

### Requirement: Unknown cost centers MUST be handled deterministically
The tool MUST handle unknown cost center identifiers as a deterministic lookup failure.

#### Scenario: Unknown cost center lookup
- **WHEN** `cost_center_id` does not exist in budget reference data
- **THEN** the tool MUST return a structured lookup failure that can be consumed by the caller without an unhandled exception
