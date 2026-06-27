---
name: column-trace
description: Trace one field through the full stack
category: analysis
inputs:
  required:
    - field
  optional:
    - --provider
    - --dry-run
providers:
  claude:
    slash_command: /column-trace
  codex:
    invocation: column-trace
  gemini:
    invocation: column-trace
  open_source:
    manifest_id: column-trace
---

# /column-trace

## What It Does

Trace one field through the full stack. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `analysis-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: field.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/column-trace <field>
/column-trace <field> --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
