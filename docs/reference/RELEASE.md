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

Release owner: `core@nunneri.com`.

Temporary fallback until Nunneri domain email is active: `yamini.sk@suranku.com`.

Commercial license and trademark-impacting release decisions require Nunneri Core Team approval.

## Branch Strategy

- `main`: default integration branch for feature and fix PRs. It must always pass validation.
- `feature/<issue-number>-short-description`: new assets, docs, installer changes, workflows, examples, and non-release enhancements.
- `fix/<issue-number>-short-description`: bug fixes and small corrections.
- `release/vX.Y.Z`: short-lived stabilization branch cut from `main` for internal releases.
- `vX.Y.Z`: release tag created from a commit contained in `release/vX.Y.Z`.

Do not use `develop` or `master` for this repository. The asset package is small enough that `main` plus short-lived release branches keeps the release process clear without adding another permanent integration branch.

## Versioning Rules

Update `VERSION` and `CHANGELOG.md` before tagging.

The GitHub release workflow requires the tag version to match `VERSION`. For example, tag `v0.1.0` requires `VERSION` to contain `0.1.0`.

## Changelog Rules

Every release-targeted issue must be represented in `CHANGELOG.md`.

## Adapter Compatibility

Claude, Codex, Gemini, open-source, and LangGraph outputs must build from the same canonical assets.

## Release Checklist

1. Confirm planned issues are accepted and linked to merged PRs.
2. Cut `release/vX.Y.Z` from `main`.
3. Update `VERSION` and `CHANGELOG.md`.
4. Run validation, adapter builds, docs sync, consumer install checks, and package checks.
5. Confirm `ARCHITECTURE.md`, `DEFENSIVE_PUBLICATION.md`, `LICENSE`, `COMMERCIAL_LICENSE.md`, `TRADEMARKS.md`, `MAINTAINERS.md`, `GOVERNANCE.md`, `SECURITY.md`, `ROADMAP.md`, `CITATION.cff`, `NOTICE.md`, and `CONTRIBUTOR_LICENSE_AGREEMENT.md` are present and synced to reference docs.
6. Create a release PR from `release/vX.Y.Z` back to `main`.
7. After approval, tag the release branch with `vX.Y.Z`.
8. Push the release branch and tag.
9. Confirm GitHub Actions publishes the internal prerelease with dist archives.
10. Merge release branch changes back to `main` if the branch contains release-only commits.

## Internal Dist Release Flow

```bash
git checkout main
git pull
git checkout -b release/v0.1.0
```

Update `VERSION` and `CHANGELOG.md`, then run:

```bash
python3 scripts/validate.py
python3 scripts/build_adapters.py
python3 scripts/build_portal_manifest.py
python3 scripts/sync_docs_reference.py
python3 scripts/check_docs_links.py
python3 scripts/check_context_exports.py
python3 scripts/check_langgraph_exports.py
python3 scripts/check_consumer_install.py
python3 scripts/package_release.py
python3 scripts/check_release_package.py
python3 scripts/check_release_ready.py --local-only
```

Optional archival step after the GitHub prerelease is published: archive the release with Zenodo or another durable archive and update `CITATION.cff` with the DOI in the next patch release.

After review and approval:

```bash
git tag v0.1.0
git push origin release/v0.1.0
git push origin v0.1.0
```

The `Internal Dist Release` workflow publishes a GitHub prerelease with:

```text
nunneri-ai-assets-0.1.0.zip
nunneri-ai-assets-0.1.0.tar.gz
nunneri-ai-assets-0.1.0.sha256
```

Manual workflow dispatch is also supported for internal release reruns, but the requested version must match `VERSION`.

## Rollback Strategy

Revert the release commit or publish a patch release that restores the previous adapter contract.

## Deprecation Policy

Mark deprecated assets in canonical metadata for one minor release before removal.
