---
name: impact-analysis
description: Trace forward lineage from a table to downstream consumers
category: analysis
inputs:
  required:
    - table
    - name
  optional:
    - --provider
    - --dry-run
providers:
  claude:
    slash_command: /impact-analysis
  codex:
    invocation: impact-analysis
  gemini:
    invocation: impact-analysis
  open_source:
    manifest_id: impact-analysis
runtimes:
  langgraph:
    enabled: true
---

# /impact-analysis

## What It Does

Trace forward lineage from a table to downstream consumers. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `analysis-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: table, name.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/impact-analysis <table> <name>
/impact-analysis <table> <name> --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
