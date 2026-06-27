> Generated from `assets/commands/triage/devhub-fix.md`.

# /devhub-fix

## What It Does

Fix a governance finding with test-first workflow and PR. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `triage-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: JSON.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/devhub-fix <JSON>
/devhub-fix <JSON> --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
