---
name: pipeline-health
description: Check chain completeness and gaps for a domain
category: operations
inputs:
  required:
    - domain
  optional:
    - --provider
    - --dry-run
providers:
  claude:
    slash_command: /pipeline-health
  codex:
    invocation: pipeline-health
  gemini:
    invocation: pipeline-health
  open_source:
    manifest_id: pipeline-health
runtimes:
  langgraph:
    enabled: true
---

# /pipeline-health

## What It Does

Check chain completeness and gaps for a domain. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `operations-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: domain.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/pipeline-health <domain>
/pipeline-health <domain> --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
