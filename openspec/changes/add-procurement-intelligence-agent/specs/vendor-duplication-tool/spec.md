## ADDED Requirements

### Requirement: Vendor duplication tool SHALL enforce contracted-vendor constraints
The system SHALL provide a tool named `check_vendor_duplication`.
Input contract: the tool MUST accept `vendor_id`, `purchase_category`, and optionally `total_amount`.
Return contract: the tool MUST return a structured result containing `requested_vendor_id`, `purchase_category`, `policy_id`, `threshold_amount`, `has_active_contract_conflict`, `deny_triggered`, `conflicting_vendor_ids`, `conflicting_contracts`, and `message`.

#### Scenario: Active contracted vendor conflict found
- **WHEN** a request uses a non-contracted vendor in a category with active contract coverage
- **THEN** the tool SHALL return the list of conflicting active vendor IDs and contract details

#### Scenario: POL-001 deny threshold triggered
- **WHEN** active contract conflicts exist and `total_amount` is at or above the POL-001 threshold for a non-contracted requested vendor
- **THEN** `deny_triggered` SHALL be `true`

#### Scenario: Conflict exists but deny is not triggered
- **WHEN** active contract conflicts exist but POL-001 deny criteria are not fully met
- **THEN** `deny_triggered` SHALL be `false`

#### Scenario: No duplication conflict in category
- **WHEN** no active contract exists for other vendors in the category
- **THEN** `has_active_contract_conflict` SHALL be `false` and `conflicting_vendor_ids` SHALL be empty
