---
name: ddl-impact
description: Assess blast radius for a table DDL change
category: analysis
inputs:
  required:
    - table
  optional:
    - --provider
    - --dry-run
providers:
  claude:
    slash_command: /ddl-impact
  codex:
    invocation: ddl-impact
  gemini:
    invocation: ddl-impact
  open_source:
    manifest_id: ddl-impact
runtimes:
  langgraph:
    enabled: true
---

# /ddl-impact

## What It Does

Assess blast radius for a table DDL change. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `analysis-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: table.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/ddl-impact <table>
/ddl-impact <table> --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
