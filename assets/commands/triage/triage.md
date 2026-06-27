---
name: triage
description: Detect stack and dispatch to the right specialist
category: triage
inputs:
  required:
    - TICKET-ID
    - symptom
  optional:
    - --provider
    - --dry-run
providers:
  claude:
    slash_command: /triage
  codex:
    invocation: triage
  gemini:
    invocation: triage
  open_source:
    manifest_id: triage
---

# /triage

## What It Does

Detect stack and dispatch to the right specialist. It routes the request through the provider-neutral asset model and only applies provider-specific behavior at the adapter layer.

## Activated Agents

- Primary: `triage-specialist` where available
- Supporting: `impact-analyst`, `release-ops-analyst`

## Inputs

Required inputs: TICKET-ID, symptom.

Optional flags: `--provider`, `--dry-run`, `--json`.

## Examples

```text
/triage <TICKET-ID> <symptom>
/triage <TICKET-ID> <symptom> --provider codex
```

## Expected Output

- Request classification
- Evidence gathered
- Recommended next action
- Approval gates
- Validation plan

## Provider Notes

Claude uses slash command Markdown, Codex and Gemini use prompt/workflow invocation metadata, and open-source frameworks use exported manifests.
