# Release Strategy

## Release Philosophy

Ship stable provider-neutral assets, generated provider adapters, and runtime exports together.

## Semantic Versioning

- Patch: documentation fixes, prompt wording changes, non-breaking adapter fixes
- Minor: new agents, skills, commands, workflows, provider adapters, or runtime adapters
- Major: breaking frontmatter, installer, invocation, or adapter contract changes

## Release Cadence

Monthly by default, with ad hoc patch releases for urgent fixes.

## Release Roles

Release owner: yamini.sk@suranku.com.

## Branch Strategy

- Default branch: `main`
- Feature: `feature/<issue-number>-short-description`
- Fix: `fix/<issue-number>-short-description`
- Release: `release/vX.Y.Z`
- Tags: `vX.Y.Z`

## Versioning Rules

Update `VERSION` and `CHANGELOG.md` before tagging.

## Changelog Rules

Every release-targeted issue must be represented in `CHANGELOG.md`.

## Adapter Compatibility

Claude, Codex, Gemini, open-source, and LangGraph outputs must build from the same canonical assets.

## Release Checklist

1. Confirm planned issues are accepted and linked to merged PRs.
2. Run validation and adapter builds.
3. Run project-level installs.
4. Update `CHANGELOG.md`.
5. Run `scripts/prepare_release.py`.
6. Create release commit.
7. Ask before tagging.
8. Ask before pushing tags or creating GitHub releases.

## Rollback Strategy

Revert the release commit or publish a patch release that restores the previous adapter contract.

## Deprecation Policy

Mark deprecated assets in canonical metadata for one minor release before removal.
