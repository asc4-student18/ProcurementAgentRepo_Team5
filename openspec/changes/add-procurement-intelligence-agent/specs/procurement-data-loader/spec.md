## ADDED Requirements

### Requirement: Data loader SHALL provide canonical access to mock datasets
The system SHALL provide loader functions in `data/loader.py` to retrieve budgets, vendors, policies, and sample requests used by tools and tests.

#### Scenario: Loader returns budgets data
- **WHEN** budget data is requested through the loader
- **THEN** the loader SHALL return structured budget records including cost center identifiers and remaining budget values

#### Scenario: Loader returns policies and vendor data
- **WHEN** policy and vendor datasets are requested
- **THEN** the loader SHALL return structured records preserving policy identifiers, thresholds, contract status, and compliance flags

### Requirement: Tools and tests MUST use loader abstraction only
Tool implementations and tests MUST access mock procurement data via `data/loader.py` and MUST NOT read files in `mock_data/` directly.

#### Scenario: Tool accesses data through loader
- **WHEN** any procurement tool evaluates a request
- **THEN** it SHALL call loader interfaces to obtain required reference data

#### Scenario: Direct mock file access disallowed
- **WHEN** code attempts to read `mock_data/*.json` directly from tool logic
- **THEN** the implementation SHALL be considered non-compliant with this capability