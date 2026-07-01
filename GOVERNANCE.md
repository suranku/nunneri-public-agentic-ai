# Governance

Nunneri was originated by Suranku and Yamini and is stewarded by the Nunneri Core Team.

This document defines how the public project makes decisions while preserving the AGPLv3 Community Edition plus commercial licensing model.

## Project Roles

## Originators

The originators are Suranku and Yamini. They hold final decision authority for project direction, ownership language, trademark usage, licensing posture, and commercial licensing strategy.

## Nunneri Core Team

The Nunneri Core Team maintains the public repository, reviews release readiness, approves sensitive changes, and manages community contributions.

Core responsibilities:

- maintain canonical assets and generated adapters
- review runtime contract changes
- approve release branches and tags
- enforce security, license, trademark, and CLA rules
- maintain public documentation and defensive-publication records

## Contributors

Contributors propose changes through GitHub Issues and pull requests. Every contribution must acknowledge the Nunneri Contributor License Agreement in `CONTRIBUTOR_LICENSE_AGREEMENT.md`.

## Decision Process

Normal technical changes follow this flow:

```text
issue -> accepted scope -> branch -> pull request -> validation -> CODEOWNERS review -> merge
```

Sensitive changes require Nunneri Core Team approval:

- license, commercial-license, CLA, notice, or ownership text
- trademark and brand usage
- security policy or vulnerability handling
- release process and release artifacts
- defensive publication, architecture, or patent-option language
- runtime contract compatibility changes
- authentication, RBAC, tenant isolation, approval gates, or provider key handling

## Runtime Contract Stewardship

The neutral Nunneri Runtime Contract is the project control plane. Runtime adapters must consume the neutral contract rather than provider-specific files.

Compatibility expectations:

- canonical assets remain the source of truth
- generated `dist/` output remains reproducible
- human approval nodes must preserve blocking approve/reject semantics
- rejection must not continue to downstream implementation nodes
- runtime-specific SDK fields belong in adapter outputs, not canonical assets

## Community and Commercial Boundaries

The public repository is the AGPLv3 Community Edition. Commercial licensing is available for organizations that need closed-source, embedded, proprietary, SaaS, OEM, managed-service, indemnity, or enterprise procurement terms.

Community features and commercial terms may evolve, but public documentation must not imply unrestricted proprietary use under the AGPLv3 Community Edition.

## Conflict Resolution

If reviewers disagree, the Nunneri Core Team decides. For license, trademark, ownership, commercial, or patent-option questions, the originators have final authority.

## Contacts

Preferred contact: `core@nunneri.com`

Temporary fallback until Nunneri domain email is active: `yamini.sk@suranku.com`
