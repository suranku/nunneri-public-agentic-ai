# .github/workflows

This directory is part of the Nunneri AI Assets repository.

## Workflows

- `validate.yml` runs on `main`, `release/**`, and PRs into those branches.
- `release.yml` publishes internal GitHub prereleases for `vX.Y.Z` tags or approved manual dispatch runs.

Release tags must match `VERSION` and tag commits must be contained in the corresponding `release/vX.Y.Z` branch.
