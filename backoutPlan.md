# Backout Plan: Procurement Intelligence Agent

**Control**: ITC.013 Backout Plan
**Component**: Procurement and Vendor Intelligence Agent (Track A Capstone)
**Repository**: [GitLab repository URL]
**Last Updated**: [fill in before Session 4 peer review]
**Prepared By**: [team name]

---

## 1. Stable Baseline

Fill this section in during Session 4 after the peer review is complete
and the test suite is passing.

| Field | Value |
|-------|-------|
| Last stable commit hash | [run: `git log --oneline -1`] |
| Last stable tag / version | [fill in if tagged; otherwise use commit hash] |
| Date of last stable state | |
| Verified by | |

---

## 2. Scope of This Component

The Procurement Intelligence Agent is a standalone advisory tool. It reads from
`mock_data/` through `data/loader.py` and writes to no external systems.
Reverting this agent does not affect any downstream services or databases.

**Files owned by this component (reverted on rollback):**

- `agent.py`
- `models.py`
- `data/loader.py`
- `tools/budget.py`
- `tools/vendor_duplication.py`
- `tools/policy_compliance.py`
- `tools/risk_assessment.py`
- `tests/`
- `openspec/` (spec files)
- `docs/rapid-peer-review.md`
- `docs/test-results.xml`
- `docs/go-no-go-checklist.md`
- `backoutPlan.md` (this file)

**Files that are read-only and are NOT reverted:**

- `mock_data/`: reference fixtures, never modified by the agent

---

## 3. Revert Procedure

### Step 1: Confirm a revert is needed

Before reverting, verify:

- [ ] The issue is reproducible against the current commit (run `pytest tests/ -v`)
- [ ] The issue is not caused by an external factor (expired API key, network outage, Python version mismatch)
- [ ] At least one group member has reviewed the failing test output

### Step 2: Identify the target commit

```bash
git log --oneline -10
# Identify the last commit where all tests passed
```

### Step 3: Revert

**Option A. Revert a specific bad commit (preferred; preserves history):**

```bash
git revert <bad-commit-hash>
# Git opens an editor for the commit message; save and close
git push origin <branch-name>
```

**Option B. Reset to a known-good commit (use only if Option A is not feasible):**

```bash
git reset --hard <known-good-commit-hash>
git push origin <branch-name> --force-with-lease
# Note: force-with-lease is safer than --force; it aborts if the remote
# has commits you haven't seen, preventing accidental data loss
```

### Step 4: Verify the revert

```bash
# Activate the virtual environment
source .venv/Scripts/activate

# Run the full test suite and capture results
pytest tests/ -v --tb=short --junitxml=docs/test-results.xml

# Confirm all tests pass before declaring the revert complete
```

### Step 5: Document the incident

Update this section after completing the revert:

| Field | Value |
|-------|-------|
| Date of incident | |
| Reverted from commit | |
| Reverted to commit | |
| Root cause | |
| Follow-up actions | |

---

## 4. Cross-Impact Statement

This agent is advisory and writes to no production systems. In the capstone
context, reverting it affects no downstream teams or services.

If this agent is later deployed as a FastAPI service or integrated into a CI/CD
pipeline, list the consumers here and notify them before reverting:

**Downstream consumers**: None in capstone context.
[Add here if integrated into a broader pipeline after the capstone.]

---

## 5. Contacts

| Role | Name | Contact |
|------|------|---------|
| Release Manager / Decision Maker | | |
| Technical Lead | | |
| Instructor / Supervisor | | |

---

*This document satisfies FedEx RAPID Framework control ITC.013 (Backout Plan).*
*Update this file before the Session 4 peer review and any time the deployment*
*or revert procedure changes.*
