---
name: nfr-readiness
description: Produce EH and logging readiness heatmap for a domain
category: compliance
inputs:
  required:
    - domain
  optional:
    - --provider
    - --dry-run
providers:
  claude:
    slash_command: /nfr-readiness
  codex:
    invocation: nfr-readiness
  gemini:
    invocation: nfr-readiness
  open_source:
    manifest_id: nfr-readiness
runtimes:
  langgraph:
    enabled: true
---

# /nfr-readiness

## What It Does

Produce EH and logging readiness heatmap for a domain. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `compliance-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: domain.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/nfr-readiness <domain>
/nfr-readiness <domain> --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
