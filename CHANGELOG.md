# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added

- Security, governance, roadmap, and citation metadata for public project trust.

### Changed

### Fixed

### Deprecated

### Removed

### Security

## [0.1.0] - 2026-07-01

### Added

- Initial provider-neutral asset library for Claude Code, Codex, Gemini, and open-source prompt exports.
- Neutral Nunneri Runtime Contract under `dist/nunneri-runtime/`.
- Runtime adapter exports for LangGraph, CrewAI, AutoGen, and Semantic Kernel.
- LangGraph runtime support with human-blocking approval gates and approve/reject resume endpoints.
- Nunneri Graph Studio UI for workflow phase config, run traces, approval cards, and per-stage outputs.
- Repository agent instruction template that renders provider-native `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`.
- Context-only installer mode, runtime install targets, dry-run support, and consumer install smoke checks.
- End-user LangGraph setup guide and interactive setup demos.
- AGPLv3 Community Edition plus commercial-license posture.
- Architecture and defensive-publication records for the runtime-neutral control plane.

### Changed

- Repositioned runtime frameworks as orchestration adapters, not model providers.
- Updated public docs and portal around originatorship, commercial licensing, and defensive publication.
- Strengthened release branch strategy with `main + release/vX.Y.Z` and prerelease artifacts.

### Security

- Added documented human approval semantics for gate nodes and rejection cancellation behavior.
