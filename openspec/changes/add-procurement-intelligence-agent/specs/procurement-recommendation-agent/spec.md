## ADDED Requirements

### Requirement: Agent SHALL use four procurement tools before finalizing recommendation
The system SHALL orchestrate `check_budget`, `check_vendor_duplication`, `check_policy_compliance`, and `assess_risk` for each valid purchase request before selecting a final decision.

#### Scenario: Full tool sequence executes
- **WHEN** a valid purchase request is submitted
- **THEN** the agent SHALL execute all four tools and collect their findings for decision resolution

#### Scenario: Partial tool failure still yields recommendation
- **WHEN** one or more tools return structured errors
- **THEN** the agent SHALL still return a recommendation and include failure details in rationale

### Requirement: Decision resolution SHALL apply priority escalate > deny > approve
The agent SHALL map combined tool and policy findings to a final decision using deterministic precedence where `escalate` overrides `deny`, and `deny` overrides `approve`.

#### Scenario: Escalation and denial signals coexist
- **WHEN** findings contain both escalation-triggering and denial-triggering conditions
- **THEN** the final decision SHALL be `escalate`

#### Scenario: Denial without escalation
- **WHEN** findings include denial-triggering violations and no escalation trigger
- **THEN** the final decision SHALL be `deny`

#### Scenario: No blocking findings
- **WHEN** findings show compliant, in-budget, low-risk conditions
- **THEN** the final decision SHALL be `approve`

### Requirement: Recommendation rationale SHALL be specific and non-empty
The final recommendation rationale MUST include specific references to relevant check outcomes, policy IDs when applicable, and any tool failures that influenced the result.

#### Scenario: Policy-driven denial rationale
- **WHEN** final decision is policy-driven denial
- **THEN** rationale SHALL reference the triggering policy finding(s)

#### Scenario: Error-aware escalation rationale
- **WHEN** final decision includes uncertainty from tool errors
- **THEN** rationale SHALL explicitly mention the affected check and the conservative handling path

### Requirement: Agent output SHALL use structured typed contract
The Pydantic AI agent SHALL be configured with `output_type=ProcurementRecommendation` so result payloads conform to the recommendation schema.

#### Scenario: Structured output returned
- **WHEN** the agent completes recommendation generation
- **THEN** `result.data` SHALL be a validated `ProcurementRecommendation` instance rather than a raw string or untyped dict

### Requirement: A second agent SHALL draft requestor email replies from recommendation output
The system SHALL provide a second Pydantic AI agent that accepts request context and a `ProcurementRecommendation`, and returns a structured `RequestorEmailDraft`.

#### Scenario: Email draft uses recommendation context
- **WHEN** a recommendation is produced for a purchase request
- **THEN** the email drafting agent SHALL receive the request details, decision, confidence score, and rationale in its prompt context

#### Scenario: Chained execution runs recommendation before email drafting
- **WHEN** the chained orchestration flow is invoked
- **THEN** recommendation generation SHALL execute first and email drafting SHALL execute second using the generated recommendation

### Requirement: Recommendation flow SHALL support incremental rationale streaming
The system SHALL expose a streaming recommendation path using the Pydantic AI streaming API so rationale text can be emitted incrementally for large or complex requests.

#### Scenario: Streaming emits rationale chunks during generation
- **WHEN** the caller invokes the streaming recommendation path for a valid request
- **THEN** rationale text SHALL be yielded in incremental chunks before final completion

#### Scenario: Streaming path still returns structured recommendation
- **WHEN** streaming generation completes
- **THEN** the final output SHALL still validate as `ProcurementRecommendation`