# Claude Repository Context

> Generated from `assets/context/repo-agent-instructions.md`. Edit the canonical context template, then rebuild adapters.

## Repository Identity and Ownership

- Repository: set the repository name here.
- Owner: set the owning team or maintainer here.
- Primary domain: describe the business or platform area.
- Primary contacts: link team channel, issue tracker, on-call page, or ownership doc.

## Golden Setup, Build, and Test Commands

- Setup: document the standard dependency installation command.
- Build: document the standard build command.
- Test: document the standard unit and integration test commands.
- Validation: document required lint, static analysis, schema, security, or release checks.
- Local services: list required local services, ports, credentials, and safe defaults.

## Common Library and Source-Code Links

- Add links to shared libraries, generated clients, framework extensions, schemas, and platform contracts.
- Prefer repository-relative paths for local code and canonical URLs for external source of truth.
- Include ownership or escalation notes when a shared dependency is outside this repository.

## Known Issues and Recurring Failure Modes

- Record known flaky tests, framework quirks, migration hazards, data issues, and operational failure modes.
- Include detection signals, safe workarounds, and links to tracking issues.
- Do not treat a known issue as permission to ignore a failing check unless an explicit override says so.

## DevOps and Environment Overrides

- List environment-specific rules for CI, deployment, secrets, feature flags, queues, topics, databases, and cloud resources.
- Call out commands that are forbidden, require approval, or must run only in sandboxed environments.
- Include rollback, cleanup, and operational safety notes for changes that affect runtime infrastructure.

## Agentic Workflow Overrides

- State repo-specific workflow changes that should be applied before dispatching an agent or command.
- Keep global workflow gates intact unless the override explicitly strengthens them.
- Repo overrides must not weaken human approval gates for code changes, publishing, production access, or release-impacting operations.

## Exception Handling and Escalation Rules

- Define exceptions to normal workflow, including emergency fixes, read-only investigations, production incidents, and compliance holds.
- Each exception should describe trigger conditions, allowed actions, required evidence, approver, and expiration or review policy.
- If an exception conflicts with provider-neutral governance, stop and ask for human approval.

## Skill Invocation Overrides

- Map repo-specific file patterns, services, languages, or commands to preferred skills.
- Use overrides to add context before a skill runs, not to bypass the skill's safety rules.
- When multiple skills match, prefer the most specific repo override, then the canonical command or workflow default.

## Agent Dispatch Rules Before Task Routing

- Load this repository instruction file before selecting a specialized agent.
- Apply known issues, DevOps overrides, exceptions, and skill overrides before dispatch.
- If a task matches a restricted area, stop at the appropriate approval gate before changing files or running side-effectful commands.

## Approval Gates and Release-Impact Rules

- Require explicit human approval before implementation changes, production-affecting commands, release tagging, publishing, or pushing.
- Summarize changed files, validation results, release impact, rollback notes, and open risks before release-impacting actions.
- For read-only work, complete evidence gathering and stop with findings unless the user explicitly authorizes changes.

## Structured Override Registry

```yaml
repo_agent_instructions:
  version: 1
  known_issues: []
  devops_overrides: []
  library_sources: []
  workflow_overrides: []
  exceptions: []
  skill_overrides: []
  dispatch_overrides: []
  approval_gates:
    - name: implementation_changes
      required: true
      applies_to:
        - code_changes
        - generated_outputs
        - release_metadata
    - name: production_or_release_actions
      required: true
      applies_to:
        - production_access
        - push
        - pull_request
        - release_tag
        - publish
```
