# Agent Behavioral Guidelines: Procurement Agent Project

These instructions apply to autonomous agent sessions working in this repository.

## Scope Constraints
- Do not modify files in `mock_data/`. These are reference data fixtures, not editable configuration.
- Do not modify `pyproject.toml` unless explicitly instructed to add or remove a dependency
- Do not create files outside the established project structure without confirming first

## Specification Discipline
- Before implementing any new model, tool, or agent component, verify a spec exists for it in `openspec/`
- If no spec exists, stop and ask before proceeding
- After implementation, run `openspec validate` and report whether the implementation matches the spec

## Code Quality Gates
- All new code must include type hints
- All new tool functions must have a docstring. The agent relies on docstrings to select tools correctly.
- Do not leave `# TODO` comments in submitted code. Complete the implementation or raise the gap explicitly.

## Testing
- Do not mark a task complete if tests are failing
- Do not delete existing tests to make a suite pass

## RAPID DevSecOps Constraints

- Every commit message must begin with a user story ID from `user-stories.md`
  in the format `[US-XXX]`. Do not commit without one.
- When running tests before a code review or Go/No-Go, use:
  `pytest tests/ -v --tb=short --junitxml=docs/test-results.xml`
  and include `docs/test-results.xml` in the commit.
- Do not modify `backoutPlan.md` to remove steps or contacts. Only append or update.
  Keep the stable baseline commit hash current after each session that ends with
  a passing test suite.
