## ADDED Requirements

### Requirement: Risk assessment tool SHALL return a vendor risk profile
The system SHALL provide a tool named `assess_risk`.
Input contract: the tool MUST accept `vendor_id`.
Return contract: the tool MUST return `vendor_id`, `compliance_flag`, `contract_status`, and `risk_level`.

#### Scenario: Active unflagged vendor risk
- **WHEN** vendor has `contract_status=active` and `compliance_flag=false`
- **THEN** `risk_level` SHALL be `low`

#### Scenario: Non-contracted vendor risk
- **WHEN** vendor has `contract_status=none` and `compliance_flag=false`
- **THEN** `risk_level` SHALL be `medium`

#### Scenario: Expired contract vendor risk
- **WHEN** vendor has `contract_status=expired` and `compliance_flag=false`
- **THEN** `risk_level` SHALL be `high`

#### Scenario: Compliance-flagged vendor risk
- **WHEN** vendor has `compliance_flag=true`
- **THEN** `risk_level` SHALL be `critical`

#### Scenario: Unknown vendor handling
- **WHEN** `vendor_id` does not exist in reference data
- **THEN** the tool MUST raise a structured lookup failure that can be handled by the caller
