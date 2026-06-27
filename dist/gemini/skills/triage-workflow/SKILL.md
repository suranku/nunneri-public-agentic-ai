> Generated from `assets/skills/triage-workflow/SKILL.md`.

---
name: triage-workflow
description: Universal Triage Workflow
category: skill
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

# Universal Triage Workflow

Use this skill whenever an agent handles a bug, incident, failing validation, or governance finding that may require diagnosis or a fix.

Follow the canonical nine-phase workflow in `assets/workflows/triage-nine-phase.md`.

## Phase Checklist

1. Intake
2. Context Load
3. Classification
4. Evidence Collection
5. Root Cause Analysis
6. Gate 1: RCA and Fix Plan Approval
7. Test-First Fix
8. Validation
9. Gate 2: Summary and Release Impact

## Gate Rules

Gate 1 is mandatory before edits. Present the RCA, evidence, fix plan, expected files, test plan, and risks. Wait for explicit approval.

Gate 2 is mandatory before commit, push, PR creation, tag, or publish. Present what changed, validation results, provider impact, release impact, compatibility notes, and recommended commit or PR text.

## Read-Only Triage

If the user asks for diagnosis only, complete phases 1 through 6 and stop. Do not edit files, create tests, or run fix phases unless the user approves implementation.

## Fix-Capable Triage

If the user approves a fix, create or update a failing test or equivalent validation before implementing. Keep the fix minimal and run checks appropriate to the stack and asset type.

## Provider-Neutral Rule

Change canonical assets first. Rebuild provider outputs after canonical asset changes. Do not hand-edit generated `dist/` files unless debugging the adapter builder itself.

## Required Output

Every triage response should report:

- Current phase
- Classification
- Evidence gathered
- Approval gate status
- Validation status
- Remaining risk
