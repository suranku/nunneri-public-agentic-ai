---
name: triage-nine-phase
description: Nine Phase Triage Workflow
category: workflow
providers:
  claude:
    enabled: true
  codex:
    enabled: true
  gemini:
    enabled: true
  open_source:
    enabled: true
runtimes:
  langgraph:
    enabled: true
---

# Nine Phase Triage Workflow

Use this workflow for bug reports, incidents that may require code changes, and governance findings such as `/devhub-fix`.

The workflow has exactly nine phases. Keep the phase count stable so teams can teach, audit, and compare triage runs consistently. Add detail as substeps inside phases instead of adding new top-level phases.

## Phase 1 - Intake

Capture the request, ticket or incident id, affected environment, symptom, expected behavior, actual behavior, user impact, and any error text.

Output:

- Triage summary
- Known facts
- Missing information
- Initial severity guess

## Phase 2 - Context Load

Read the repo context and provider context before inspecting code. Prefer provider-neutral context first, then provider-specific context when relevant.

Context order:

1. `AI_ASSETS.md`
2. Provider context such as `CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`
3. Project README and build/test documentation
4. Relevant command, skill, or workflow assets

Output:

- Applicable provider
- Applicable stack
- Relevant local conventions
- Constraints that affect the fix

## Phase 3 - Classification

Classify the issue before changing files.

Classification options:

- Code
- Configuration
- Data
- Schema
- Infrastructure
- Dependency
- Framework or runtime
- Documentation or asset metadata
- Unknown

Output:

- Primary classification
- Secondary classification, if any
- Why other likely classifications were ruled out

## Phase 4 - Evidence Collection

Gather enough evidence to support or reject a root cause. Do not implement a fix in this phase.

Evidence sources:

- Stack traces and logs
- Failing tests or reproduction steps
- Code search
- Git history
- Configuration and environment differences
- Schema or contract changes
- Provider adapter output, if the bug is asset-related

Output:

- Evidence table
- Files inspected
- Commands run
- Reproduction status

## Phase 5 - Root Cause Analysis

State the root cause as a testable claim. Separate confirmed evidence from assumptions.

Output:

- Root cause
- Confidence level
- Blast radius
- Proposed fix
- Proposed validation
- Risks and rollback notes

## Phase 6 - Gate 1: RCA and Fix Plan Approval

Stop and wait for explicit human approval before changing implementation files, provider assets, generated outputs, or release metadata.

The approval request must include:

- Root cause
- Evidence
- Fix plan
- Test plan
- Files expected to change
- Risks

Allowed before approval:

- Read files
- Search
- Run non-mutating diagnostics
- Draft a plan

Not allowed before approval:

- Edit files
- Commit
- Push
- Open a PR
- Tag or publish a release

## Phase 7 - Test-First Fix

After approval, create or update a failing test, assertion, fixture, or validation case that demonstrates the bug. If a failing test is not feasible, document why and use the smallest equivalent validation.

Then implement the smallest correct fix.

Output:

- Test or validation added
- Fix implemented
- Files changed
- Any deviation from test-first workflow

## Phase 8 - Validation

Run the relevant checks for the stack and asset type.

Common checks:

- Unit or integration tests
- Static analysis or linting
- Coverage check, when available
- `python3 scripts/validate.py` for this asset repo
- `python3 scripts/build_adapters.py` when canonical assets changed
- `python3 scripts/build_portal_manifest.py` when portal data changed
- `python3 scripts/sync_docs_reference.py` when public docs changed

Output:

- Commands run
- Results
- Coverage or quality gate status
- Remaining risk

## Phase 9 - Gate 2: Summary and Release Impact

Stop and present the final validation summary before committing, pushing, opening a PR, tagging, or publishing.

The summary must include:

- What changed
- Validation results
- Release impact
- Provider impact
- Backward compatibility notes
- Recommended commit message
- Recommended PR body or changelog entry

## Post-Triage Actions

Commit, push, PR creation, release tagging, and publishing are outside the nine phases. They require explicit human confirmation even when Phase 9 passes.

## Read-Only Mode

For read-only triage, complete phases 1 through 6 and stop after Gate 1 with an RCA and recommended plan. Do not run phases 7 through 9 unless the user explicitly approves a fix.
