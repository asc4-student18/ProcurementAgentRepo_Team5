## ADDED Requirements

### Requirement: Purchase request input schema SHALL be strictly validated
The system SHALL define a `PurchaseRequest` model with these required fields exactly as named: `request_id`, `requestor`, `cost_center_id`, `vendor_name`, `vendor_id`, `category`, `item_description`, `quantity`, `unit_price`, and `total_amount`.
The model SHALL validate all required fields before any recommendation logic executes.

#### Scenario: Valid request model accepted
- **WHEN** a purchase request includes all required fields with valid types and non-empty identifiers
- **THEN** the request SHALL be accepted as a typed `PurchaseRequest` instance for downstream checks

#### Scenario: Invalid request model rejected
- **WHEN** a purchase request omits required fields or provides invalid types/values
- **THEN** the system SHALL reject the payload and route the outcome to a refusal or escalation path instead of silently continuing

#### Scenario: Dataset-only labels are not treated as input schema fields
- **WHEN** a sample request includes `expected_outcome` or `outcome_reason` labels from test data
- **THEN** those labels SHALL be treated as test metadata and MUST NOT be required fields of `PurchaseRequest`

### Requirement: Purchase request numeric constraints SHALL be enforced with validators
The `PurchaseRequest` model MUST apply validators for numeric integrity: `quantity` MUST be an integer greater than 0, `unit_price` MUST be greater than 0, and `total_amount` MUST be greater than 0.
The model SHOULD validate that `total_amount` equals `quantity * unit_price` within a defined rounding tolerance and MUST reject requests that violate configured tolerance rules.

#### Scenario: Positive numeric inputs accepted
- **WHEN** `quantity`, `unit_price`, and `total_amount` are all positive and consistent with rounding policy
- **THEN** numeric validation SHALL pass

#### Scenario: Invalid numeric inputs rejected
- **WHEN** `quantity` is non-positive, non-integer, or price/amount fields are non-positive
- **THEN** numeric validation MUST fail with a structured validation error

#### Scenario: Inconsistent totals rejected by tolerance rule
- **WHEN** `total_amount` deviates from `quantity * unit_price` beyond allowed tolerance
- **THEN** the request MUST be rejected as schema-invalid

### Requirement: Recommendation output schema SHALL constrain decision values
The system SHALL define a `ProcurementRecommendation` model where `decision` MUST be one of `approve`, `deny`, or `escalate`, and `rationale` MUST be a non-empty string.

#### Scenario: Valid recommendation produced
- **WHEN** the agent returns a recommendation with an allowed decision and non-empty rationale
- **THEN** the output SHALL validate as `ProcurementRecommendation`

#### Scenario: Invalid decision prevented
- **WHEN** recommendation generation attempts to emit a decision outside `approve`/`deny`/`escalate`
- **THEN** output validation SHALL fail and the invalid response SHALL not be accepted as final output