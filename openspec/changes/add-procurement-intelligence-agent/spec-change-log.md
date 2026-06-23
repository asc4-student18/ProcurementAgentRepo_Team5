# Spec Change Log: add-procurement-intelligence-agent

## Purpose
This file records the delta-spec review outcomes and the follow-up modifications made in response.

## Issue/Risk and Update Log

### 1. PurchaseRequest field traceability
Issue identified:
- Field coverage in the model spec was abstract and did not enumerate exact request input field names.

Risk identified:
- Weak traceability between spec requirements and `mock_data/requests.json` schema.

Update made:
- Updated `procurement-models` spec to explicitly require these `PurchaseRequest` fields:
  - `request_id`, `requestor`, `cost_center_id`, `vendor_name`, `vendor_id`, `category`, `item_description`, `quantity`, `unit_price`, `total_amount`.
- Added a scenario clarifying `expected_outcome` and `outcome_reason` are test metadata and MUST NOT be required `PurchaseRequest` fields.

Updated file:
- openspec/changes/add-procurement-intelligence-agent/specs/procurement-models/spec.md

### 2. Numeric validation under-specification
Issue identified:
- Numeric validator expectations were not explicit for quantity, pricing, and total consistency.

Risk identified:
- Implementations could accept invalid or inconsistent numeric values.

Update made:
- Added explicit validator requirements:
  - `quantity` MUST be an integer greater than 0.
  - `unit_price` MUST be greater than 0.
  - `total_amount` MUST be greater than 0.
  - `total_amount` SHOULD match `quantity * unit_price` within tolerance and MUST be rejected when outside configured tolerance.
- Added acceptance scenarios for positive values, invalid values, and inconsistent totals.

Updated file:
- openspec/changes/add-procurement-intelligence-agent/specs/procurement-models/spec.md

### 3. Tool contract clarity gaps
Issue identified:
- Four tool requirements existed, but input contracts, return shapes, and error behavior were not equally explicit for every tool.

Risk identified:
- Inconsistent tool interfaces and weaker interoperability/integration tests.

Update made:
- Added explicit contract blocks for each tool (`check_budget`, `check_vendor_duplication`, `check_policy_compliance`, `assess_risk`) covering:
  - Required input fields.
  - Structured return fields.
  - Deterministic structured error behavior.
- Added explicit failure scenarios for unknown lookups/data unavailability.
- Added cross-tool error contract:
  - Error MUST include `code` and `message`.
  - Error SHOULD include `retryable`.
  - Tools MUST NOT propagate unhandled exceptions.

Updated file:
- openspec/changes/add-procurement-intelligence-agent/specs/procurement-evaluation-tools/spec.md

### 4. Acceptance language precision
Issue identified:
- Some wording was less deterministic for test assertions.

Risk identified:
- Ambiguity during implementation and QA acceptance decisions.

Update made:
- Tightened requirement language to RFC 2119 terms (SHALL/MUST/SHOULD).
- Reworded less testable statements (for example risk output wording) to deterministic expected outcomes.

Updated files:
- openspec/changes/add-procurement-intelligence-agent/specs/procurement-models/spec.md
- openspec/changes/add-procurement-intelligence-agent/specs/procurement-evaluation-tools/spec.md

## Validation
- Command run: openspec validate add-procurement-intelligence-agent
- Result: Change is valid

## Scope Note
This log documents specification-level updates only. No implementation code was added or modified as part of this review pass.
