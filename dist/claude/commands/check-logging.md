> Generated from `assets/commands/compliance/check-logging.md`.

# /check-logging

## What It Does

Audit logging against standards. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `compliance-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: none.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/check-logging [options]
/check-logging [options] --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
