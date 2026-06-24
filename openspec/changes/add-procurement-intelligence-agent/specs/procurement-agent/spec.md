## ADDED Requirements

### Requirement: Agent SHALL accept PurchaseRequest and return ProcurementRecommendation
The agent implementation in `agent.py` SHALL accept input compatible with `models.PurchaseRequest` and SHALL return output compatible with `models.ProcurementRecommendation`.

#### Scenario: Valid input contract is accepted
- **WHEN** the caller provides a valid `PurchaseRequest` instance or a dictionary that validates into `PurchaseRequest`
- **THEN** the agent SHALL proceed with recommendation evaluation

#### Scenario: Output contract is always structured
- **WHEN** recommendation generation completes
- **THEN** the returned object SHALL validate as `ProcurementRecommendation` with `decision` in `approve|deny|escalate` and a non-empty `rationale`

### Requirement: Agent SHALL execute four procurement tools per request
For each valid request, the orchestration in `agent.py` SHALL attempt all four checks before decision resolution:
- `check_budget`
- `check_vendor_duplication`
- `check_policy_compliance`
- `assess_risk`

#### Scenario: Full tool sequence is attempted
- **WHEN** a valid request is processed
- **THEN** all four tool calls SHALL be attempted and their findings collected

### Requirement: Decision resolution SHALL be deterministic and code-owned
Final decision logic SHALL be resolved by deterministic post-processing logic in `agent.py` and SHALL NOT rely on model-only prompt reasoning.

#### Scenario: Priority order is applied
- **WHEN** findings include one or more escalation and denial signals
- **THEN** final decision SHALL follow strict precedence `escalate > deny > approve`

#### Scenario: Denial without escalation signals
- **WHEN** findings include denial signals and no escalation signals
- **THEN** final decision SHALL be `deny`

#### Scenario: No blocking signals
- **WHEN** findings include no escalation and no denial signals
- **THEN** final decision SHALL be `approve`

### Requirement: Agent SHALL handle tool failures without crashing
Tool failures SHALL be isolated per check so that recommendation generation continues and returns a valid `ProcurementRecommendation`.

#### Scenario: Tool exception occurs
- **WHEN** any tool raises an exception during execution
- **THEN** the agent SHALL capture the error, continue remaining checks, and still return a recommendation

#### Scenario: Structured tool error is returned
- **WHEN** a tool returns an error payload instead of raising
- **THEN** the agent SHALL treat the error as a surfaced finding and include it in rationale

#### Scenario: Conservative failure handling
- **WHEN** one or more tool failures reduce confidence
- **THEN** the agent SHALL add escalation signal(s) for uncertainty and resolve final decision by the same precedence rules

### Requirement: System prompt SHALL enforce orchestration and rationale constraints
The system prompt used by the Pydantic AI `Agent` SHALL constrain behavior without replacing deterministic decision logic.

#### Scenario: Prompt constraints are present
- **WHEN** `create_procurement_agent` constructs the agent
- **THEN** the system prompt SHALL require:
  - all four checks are attempted for each valid request
  - findings are summarized faithfully and specifically
  - policy IDs are referenced when relevant
  - tool failures are disclosed in rationale
  - the response conforms to `ProcurementRecommendation`

#### Scenario: Prompt does not override resolver
- **WHEN** prompt language and deterministic resolver could conflict
- **THEN** the post-processing resolver in `agent.py` SHALL determine final decision output
