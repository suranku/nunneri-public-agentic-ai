---
name: ingestion-check
description: Trace upstream dependencies for an API endpoint
category: operations
inputs:
  required:
    - endpoint
  optional:
    - --provider
    - --dry-run
providers:
  claude:
    slash_command: /ingestion-check
  codex:
    invocation: ingestion-check
  gemini:
    invocation: ingestion-check
  open_source:
    manifest_id: ingestion-check
runtimes:
  langgraph:
    enabled: true
---

# /ingestion-check

## What It Does

Trace upstream dependencies for an API endpoint. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `operations-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: endpoint.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/ingestion-check <endpoint>
/ingestion-check <endpoint> --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
