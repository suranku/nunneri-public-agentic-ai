---
name: exception-handling
description: Run exception handling audit and static scan
category: compliance
inputs:
  required:
    []
  optional:
    - --provider
    - --dry-run
providers:
  claude:
    slash_command: /exception-handling
  codex:
    invocation: exception-handling
  gemini:
    invocation: exception-handling
  open_source:
    manifest_id: exception-handling
---

# /exception-handling

## What It Does

Run exception handling audit and static scan. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `compliance-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: none.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/exception-handling [options]
/exception-handling [options] --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
