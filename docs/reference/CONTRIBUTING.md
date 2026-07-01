# Contributing

Contributions to Nunneri AI Assets start with GitHub Issues.

Nunneri uses an AGPLv3 Community Edition plus commercial licensing model. Contributions must acknowledge the Nunneri Contributor License Agreement in `CONTRIBUTOR_LICENSE_AGREEMENT.md` so the project can continue distributing accepted contributions under both AGPLv3 and commercial terms.

## Feedback and Enhancement Workflow

```text
issue -> admin triage -> accepted scope -> branch -> PR -> CI -> CODEOWNERS approval -> release
```

## Step 1 - Open a GitHub Issue

Use the closest issue template. Include provider, asset type, impact, expected behavior, and acceptance criteria.

## Step 2 - Admin Triage to JIRA Story

Admins triage within 2 business days and may link a `NUN` story.

## Step 3 - Branch and Develop

Use `feature/<issue-number>-short-description` or `fix/<issue-number>-short-description`.

## Step 4 - Open Pull Request and CI

Every PR must link the accepted issue, include validation output, declare provider impact, and confirm CLA acceptance.

## Step 5 - CODEOWNERS Approval, Merge, and Distribute

CODEOWNERS approval is required before merge.

License, trademark, commercial-license, homepage, release, and generated-reference changes require Nunneri Core Team review.

## Issue Labels and Triage States

Use type, asset, provider, priority, and status labels from `.github/labels.yml`.

## Issue to Release Flow

Accepted issues are assigned a release target and must be referenced in `CHANGELOG.md` before release.

## Release Participation

Release owner: `core@nunneri.com`.

Temporary fallback until Nunneri domain email is active: `yamini.sk@suranku.com`.

## Contributor License Agreement

Every pull request must include this acknowledgment:

```text
I agree that my contribution is submitted under the Nunneri Contributor License Agreement.
```

Do not merge PRs that change license, trademark, commercial-use, or ownership language without CODEOWNERS approval.

## Provider Adapter Guidelines

Change canonical assets first. Adapter outputs are generated.

## Asset Frontmatter Reference

Required fields are `name`, `description`, and `category` where applicable.

## Questions

Open an issue using the feedback template.

Note: GitHub issue templates only become visible after `.github/ISSUE_TEMPLATE/` is merged to the default branch.
