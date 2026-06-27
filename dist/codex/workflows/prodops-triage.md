> Generated from `assets/commands/triage/prodops-triage.md`.

# /prodops-triage

## What It Does

Classify an incident into a known runbook or JIRA defect. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `triage-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: INC-ID, ENV, error.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/prodops-triage <INC-ID> <ENV> <error>
/prodops-triage <INC-ID> <ENV> <error> --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
