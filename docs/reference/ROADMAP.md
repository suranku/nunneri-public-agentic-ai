# Roadmap

This roadmap separates near-term Community Edition work from future commercial or enterprise options. It is directional and may change as the project matures.

## Current Focus

Nunneri is focused on a provider- and runtime-neutral control plane for agentic workflows:

- canonical assets authored once under `assets/`
- neutral runtime contract generated under `dist/nunneri-runtime/`
- provider adapters for Claude Code, Codex, Gemini, and open-source exports
- runtime adapters for LangGraph, CrewAI, AutoGen, and Semantic Kernel
- Nunneri Graph Studio for phase config, traces, node outputs, and human approvals
- durable state outside LLM context through threads, runs, checkpoints, and per-phase outputs
- RBAC and multi-tenant scoping across org, team, project, thread, run, and approval actions

## Community Edition Priorities

Planned Community Edition improvements:

- improve Graph Studio run inspection and per-stage output quality
- strengthen human approval UX for pending, approved, rejected, cancelled, and completed runs
- improve provider-key model routing and local development auth
- expand runtime contract validation and adapter smoke tests
- add more runnable runtime examples without requiring vendor SDKs by default
- improve docs for installation, migration, release packaging, and end-user setup
- keep MinIO and other object storage optional through S3-compatible adapters

## Commercial and Enterprise Options

Commercial licensing is available for teams that need proprietary usage or enterprise terms.

Potential commercial or enterprise-facing work may include:

- enterprise support and procurement terms
- deployment hardening guides
- managed-service packaging
- indemnity or negotiated licensing terms
- private adapter support for internal agent frameworks
- enterprise identity and audit integrations
- advanced governance and compliance reporting

These items are not commitments until published in a release plan or commercial agreement.

## Not Planned Now

The following are intentionally out of scope for the immediate roadmap:

- making runtime SDKs mandatory root dependencies
- treating LangGraph, CrewAI, AutoGen, or Semantic Kernel as model providers
- replacing the neutral runtime contract with provider-specific source files
- using "patent pending" language before an application is filed

## Release Planning

Internal releases use `main + release/vX.Y.Z` with `vX.Y.Z` tags. See `RELEASE.md`.

Release-targeted work should be represented in `CHANGELOG.md` before tagging.
