---
name: generate-agent-context
description: Generate or augment provider-specific repo context files
category: compliance
inputs:
  required:
    []
  optional:
    - --provider
    - --dry-run
providers:
  claude:
    slash_command: /generate-agent-context
  codex:
    invocation: generate-agent-context
  gemini:
    invocation: generate-agent-context
  open_source:
    manifest_id: generate-agent-context
---

# /generate-agent-context

## What It Does

Generate or augment provider-specific repo context files. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `compliance-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: none.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/generate-agent-context [options]
/generate-agent-context [options] --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
