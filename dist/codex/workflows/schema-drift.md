> Generated from `assets/commands/analysis/schema-drift.md`.

# /schema-drift

## What It Does

Detect breaking schema changes from the latest build. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `analysis-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: none.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/schema-drift [options]
/schema-drift [options] --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
