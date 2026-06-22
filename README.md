# Procurement and Vendor Intelligence Agent (Track A)

## Scenario

You are a development team on FedEx's Enterprise Procurement Tools group. The procurement
department processes several hundred purchase requests per week. Many of these requests are
straightforward and consume analyst time that could be better spent on complex or high-value
decisions. Your team has been asked to build a procurement intelligence agent that pre-screens
requests and produces structured recommendations (**approve**, **deny**, or **escalate**) with
written rationale that a procurement officer can act on directly.

The agent's output is advisory. The procurement officer remains the decision-maker. The agent
must be reliable, explainable, and consistent.

## Acceptance Criteria

These items are grouped by the six categories of the FedEx Capstone Rubric (v5.0).
At certification, each category must clear an 80% bar to pass; teams should target
100%. Items below each heading must be true for that category to count as met.

### Category 1: Agent functionality and correctness

- [ ] The agent accepts a `PurchaseRequest` as input and returns a `ProcurementRecommendation`
- [ ] The recommendation is always one of `approve`, `deny`, or `escalate`
- [ ] Every recommendation includes a non-empty `rationale` referencing which check(s) drove the decision
- [ ] The agent performs all four checks: budget, vendor duplication, policy compliance, risk assessment
- [ ] All three decision types are reachable using the provided sample requests in `mock_data/requests.json`
- [ ] The agent runs end to end on all 15 sample requests without crashing or unhandled exceptions
- [ ] Tool docstrings are clear enough that the agent reliably selects the correct tool for each check

### Category 2: Spec-driven design quality

- [ ] An OpenSpec change directory `openspec/changes/add-procurement-intelligence-agent/` exists, produced by `/opsx-propose`
- [ ] `openspec/changes/add-procurement-intelligence-agent/proposal.md` is coherent: states why the change is being made, what is changing (capabilities added, modified, or removed), and what the impact is
- [ ] `openspec/changes/add-procurement-intelligence-agent/specs/` contains delta specs for every capability the agent introduces (models, data loader, four tools, agent wiring) with measurable acceptance criteria
- [ ] `openspec/changes/add-procurement-intelligence-agent/design.md` documents the architectural decisions (priority of decision rules, tool selection logic, error-handling fallback path)
- [ ] `openspec/changes/add-procurement-intelligence-agent/tasks.md` lists the implementation steps and is fully checked off when implementation is complete
- [ ] `openspec validate add-procurement-intelligence-agent` (or `openspec validate --all`) passes with no structural failures
- [ ] Pydantic models match the delta spec exactly (typed fields, validators, allowed values for `decision`)
- [ ] Commit history shows the OpenSpec proposal authored before its implementation, not backfilled

### Category 3: Engineering quality

- [ ] Tool-level test coverage in `tests/` (not just the agent class)
- [ ] Tests cover decision logic and edge cases, including at least one partial-data scenario
- [ ] Tool errors have a defined fallback path: when a tool is unavailable or fails, the agent returns a partial recommendation with the failure surfaced in the rationale, not a generic error
- [ ] Schema validation on agent inputs and outputs; out-of-policy inputs trigger a refusal or escalation rather than a silent pass
- [ ] No hardcoded secrets or credentials in the repository
- [ ] Code is readable: docstrings on every public function, named constants for magic numbers, naming reflects intent
- [ ] pytest suite passes covering at minimum: approve, deny, policy-deny, and escalate

### Category 4: RAPID controls execution (ITC.009 and ITC.004)

- [ ] `docs/rapid-peer-review.md` exists with all six RAPID Code Work Product criteria rated and a summary recommendation (approved / approved with conditions / not approved)
- [ ] All Fail findings in the peer review are resolved; all Needs Attention findings are resolved or formally accepted with written rationale
- [ ] `docs/go-no-go-checklist.md` is completed with every section filled: requirements, code review, test results, outstanding issues, backout plan, decision
- [ ] The Go/No-Go Decision Rationale is evidence-backed (specific test counts, peer review rating, acceptance criteria status), not asserted

### Category 5: AI-assisted development practice

- [ ] `.github/copilot-instructions.md` is present, coherent, and reflects the project (not the starter template left untouched)
- [ ] Commit history is preserved and inspectable: no force-pushes that erased iteration, no squashed branches that hide the build sequence
- [ ] A `prompts.md` (or equivalent) in the repository captures the prompts that produced the key components
- [ ] OpenSpec proposal iteration is visible in the commit history: proposals evolved through commits, they were not backfilled at the end
- [ ] (Showcase prep) The team can name one instance where they redirected or rejected Copilot output, and why
- [ ] (Showcase prep) The team can name where Copilot helped them move faster and where they had to step in and correct it

### Category 6: Demonstration and communication

- [ ] The team delivers a 3 to 5 minute demonstration within the allotted time
- [ ] The team explains why they made specific design choices, not just what they did
- [ ] The team identifies what they would do differently with more time
- [ ] The team answers the structured debrief question live without deferring entirely to slides
- [ ] The demo is framed for a FedEx stakeholder audience, not for peers

## Project Structure

```
procurement-agent/
├── agent.py              # Main Pydantic AI agent (you build this)
├── models.py             # PurchaseRequest and ProcurementRecommendation models (you build this)
├── tools/                # Tool implementations (you build this)
├── data/
│   └── loader.py         # Mock data loader (you build this)
├── tests/                # Test suite (you build this)
├── mock_data/            # Reference data; do not modify
│   ├── budgets.json
│   ├── vendors.json
│   ├── policies.json
│   └── requests.json
├── openspec/             # Spec-driven development artifacts (you populate this)
├── docs/                 # RAPID compliance documents (provided templates)
│   ├── rapid-peer-review.md      # Generated by peer review Agent Skill
│   └── go-no-go-checklist.md     # Complete at start of Session 5
├── .github/
│   ├── copilot-instructions.md  # Project conventions (read by Copilot at runtime)
│   └── skills/
│       └── rapid-peer-review.md # RAPID peer review Agent Skill (provided)
└── prompts.md                   # Capture the prompts that produced key components (you fill in)
```

## Getting Started

See the lab guide for step-by-step instructions. Complete environment setup before Session 1.

## Data Reference

The `mock_data/` directory contains 10 cost centers, 17 vendors, 8 policies, and 15 sample
purchase requests. The requests are designed to produce all three decision outcomes. Review
`requests.json` carefully during Session 1 before writing any specification.
