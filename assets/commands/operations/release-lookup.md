---
name: release-lookup
description: Compare module versions and latest releases
category: operations
inputs:
  required:
    - latest
  optional:
    - --provider
    - --dry-run
providers:
  claude:
    slash_command: /release-lookup
  codex:
    invocation: release-lookup
  gemini:
    invocation: release-lookup
  open_source:
    manifest_id: release-lookup
runtimes:
  langgraph:
    enabled: true
---

# /release-lookup

## What It Does

Compare module versions and latest releases. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `operations-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: latest.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/release-lookup <latest>
/release-lookup <latest> --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
