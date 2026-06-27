> Generated from `assets/commands/reporting/report-lineage.md`.

# /report-lineage

## What It Does

Identify objects that feed or use a report. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `reporting-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: report.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/report-lineage <report>
/report-lineage <report> --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
