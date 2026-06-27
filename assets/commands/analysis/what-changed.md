---
name: what-changed
description: Create a changelog of new and removed objects
category: analysis
inputs:
  required:
    []
  optional:
    - --provider
    - --dry-run
providers:
  claude:
    slash_command: /what-changed
  codex:
    invocation: what-changed
  gemini:
    invocation: what-changed
  open_source:
    manifest_id: what-changed
runtimes:
  langgraph:
    enabled: true
---

# /what-changed

## What It Does

Create a changelog of new and removed objects. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `analysis-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: none.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/what-changed [options]
/what-changed [options] --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
