# Issue and Fix Log: add-procurement-intelligence-agent

## Scope
This document logs identified issues and the exact updates made to fix them across proposal artifacts.

## 1. PurchaseRequest field traceability was ambiguous
Issue:
- The model spec described fields in abstract terms and did not explicitly enumerate required request field names.

Update made to fix:
- Explicitly listed required `PurchaseRequest` fields:
  - `request_id`, `requestor`, `cost_center_id`, `vendor_name`, `vendor_id`, `category`, `item_description`, `quantity`, `unit_price`, `total_amount`.
- Added requirement/scenario clarifying `expected_outcome` and `outcome_reason` are dataset metadata and are not required input schema fields.

Updated file:
- `openspec/changes/add-procurement-intelligence-agent/specs/procurement-models/spec.md`

## 2. Numeric validation requirements were under-specified
Issue:
- Numeric validator rules were not explicit for quantity, unit price, total amount, and total consistency.

Update made to fix:
- Added normative numeric constraints:
  - `quantity` MUST be integer > 0
  - `unit_price` MUST be > 0
  - `total_amount` MUST be > 0
- Added consistency rule:
  - `total_amount` SHOULD match `quantity * unit_price` within tolerance
  - Requests outside tolerance MUST be rejected
- Added scenarios for valid numeric inputs, invalid numeric inputs, and inconsistent totals.

Updated file:
- `openspec/changes/add-procurement-intelligence-agent/specs/procurement-models/spec.md`

## 3. Tool contracts were not fully explicit across all four tools
Issue:
- Tool requirements existed but input contracts, return shapes, and error behavior were not equally explicit for each tool.

Update made to fix:
- Added explicit contract sections for each tool:
  - `check_budget`
  - `check_vendor_duplication`
  - `check_policy_compliance`
  - `assess_risk`
- Defined per-tool:
  - Required input fields
  - Required return fields
  - Structured error behavior for lookup/data failures
- Added cross-tool error contract:
  - Error MUST include `code` and `message`
  - Error SHOULD include `retryable`
  - Tools MUST NOT propagate unhandled exceptions

Updated file:
- `openspec/changes/add-procurement-intelligence-agent/specs/procurement-evaluation-tools/spec.md`

## 4. Some acceptance language was less testable
Issue:
- A few statements were too qualitative and less deterministic for testing.

Update made to fix:
- Rewrote requirements/scenarios with clearer RFC 2119 phrasing (SHALL/MUST/SHOULD).
- Tightened wording in risk-related outcomes to deterministic assertions.

Updated files:
- `openspec/changes/add-procurement-intelligence-agent/specs/procurement-models/spec.md`
- `openspec/changes/add-procurement-intelligence-agent/specs/procurement-evaluation-tools/spec.md`

## 5. tasks.md tracking was not granular enough for Sessions 2-3
Issue:
- Tool testing was bundled in one shared checkbox, making progress tracking harder.
- Data-loader error handling task used ambiguous "or" phrasing.

Update made to fix:
- Split shared tool test task into separate per-tool test checkboxes:
  - Budget tests
  - Vendor duplication tests
  - Policy compliance tests
  - Risk assessment tests
- Made data-loader error-handling task unambiguous with deterministic structured error responses.

Updated file:
- `openspec/changes/add-procurement-intelligence-agent/tasks.md`

## Validation
- Ran: `openspec validate add-procurement-intelligence-agent`
- Result: Change is valid
