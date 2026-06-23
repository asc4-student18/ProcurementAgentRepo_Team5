## ADDED Requirements

### Requirement: Budget check tool SHALL report spend feasibility
The system SHALL provide a tool named `check_budget`.
Input contract: the tool MUST accept a `PurchaseRequest` payload containing at minimum `cost_center_id` and `total_amount`.
Return contract: the tool MUST return a structured result containing `within_budget` (boolean), `remaining_budget` (number), `overage` (number), and `error` (null or structured error object).

#### Scenario: Request within budget
- **WHEN** request total amount is less than or equal to remaining budget
- **THEN** `check_budget` SHALL return `within_budget=true` and `overage=0`

#### Scenario: Request exceeds budget
- **WHEN** request total amount is greater than remaining budget
- **THEN** `check_budget` SHALL return `within_budget=false` and a positive `overage` value

#### Scenario: Unknown cost center returns structured error
- **WHEN** `cost_center_id` cannot be found in budget data
- **THEN** `check_budget` MUST return `error` with a machine-readable code and MUST NOT raise an unhandled exception

### Requirement: Vendor duplication tool SHALL enforce contracted-vendor constraints
The system SHALL provide a tool named `check_vendor_duplication`.
Input contract: the tool MUST accept a `PurchaseRequest` payload containing at minimum `vendor_id`, `category`, and `total_amount`.
Return contract: the tool MUST return a structured result containing `is_duplicate_violation` (boolean), `conflicting_vendor_ids` (array), `applied_policy_ids` (array), `violation_reason` (string or null), and `error` (null or structured error object).

#### Scenario: Active contracted vendor conflict found
- **WHEN** a request uses a non-contracted vendor in a category with active contract coverage and applicable threshold conditions
- **THEN** the tool SHALL report conflicting contracted vendor identifiers and violation context

#### Scenario: No duplication restriction violation
- **WHEN** category has no applicable single-source restriction or requested vendor is contracted
- **THEN** the tool SHALL report no duplication violation

#### Scenario: Vendor lookup failure returns structured error
- **WHEN** `vendor_id` is unknown or vendor data cannot be loaded
- **THEN** `check_vendor_duplication` MUST return `error` with a machine-readable code and MUST NOT raise an unhandled exception

### Requirement: Policy compliance tool SHALL evaluate all defined procurement policies
The system SHALL provide a tool named `check_policy_compliance`.
Input contract: the tool MUST accept a `PurchaseRequest` payload with fields needed for policy evaluation, including `category`, `total_amount`, `vendor_id`, and `cost_center_id`.
Return contract: the tool MUST return a structured result containing `violations` (array of objects with `policy_id`, `description`, `severity`, and `forced_decision`), `has_violation` (boolean), and `error` (null or structured error object).

#### Scenario: Prohibited category detected
- **WHEN** request category matches a prohibited category policy
- **THEN** the tool SHALL emit a violation entry that indicates denial is required

#### Scenario: Approval-threshold policy triggered
- **WHEN** request amount enters manager/director threshold ranges
- **THEN** the tool SHALL emit policy findings indicating required approval/escalation posture

#### Scenario: Policy dataset unavailable returns structured error
- **WHEN** policy data cannot be loaded or parsed
- **THEN** `check_policy_compliance` MUST return `error` with a machine-readable code and MUST NOT raise an unhandled exception

### Requirement: Risk assessment tool SHALL classify vendor risk posture
The system SHALL provide a tool named `assess_risk`.
Input contract: the tool MUST accept a `PurchaseRequest` payload containing at minimum `vendor_id` and `category`.
Return contract: the tool MUST return a structured result containing `compliance_flag` (boolean), `contract_status` (string), `risk_level` (one of `low`, `medium`, `high`, `critical`), `risk_reasons` (array), and `error` (null or structured error object).

#### Scenario: Compliance-flagged vendor assessed
- **WHEN** vendor has an active compliance flag
- **THEN** the tool SHALL return `risk_level` as `high` or `critical` and include the compliance signal in `risk_reasons`

#### Scenario: Normal vendor assessed
- **WHEN** vendor is active, unflagged, and contractually valid
- **THEN** the tool SHALL return low or medium risk based on available signals

#### Scenario: Vendor lookup failure returns structured error
- **WHEN** vendor metadata is unavailable for a request
- **THEN** `assess_risk` MUST return `error` with a machine-readable code and MUST NOT raise an unhandled exception

### Requirement: Tool errors SHALL be explicit and non-silent
If any tool encounters lookup failures or runtime errors, the tool response MUST provide a structured error signal consumable by the agent rationale.
Error objects MUST include at least `code` and `message` fields and SHOULD include a `retryable` boolean.

#### Scenario: Unknown cost center in budget check
- **WHEN** a request references an unknown cost center
- **THEN** the budget tool SHALL return a structured error outcome rather than crashing

#### Scenario: Vendor lookup failure in risk assessment
- **WHEN** vendor metadata is unavailable for a request
- **THEN** the risk tool SHALL return an explicit error signal for escalation-aware handling

#### Scenario: Any tool runtime exception is converted to structured error
- **WHEN** an unexpected runtime exception occurs inside any procurement tool
- **THEN** the tool MUST return an `error` object and MUST NOT propagate an unhandled exception to the agent caller