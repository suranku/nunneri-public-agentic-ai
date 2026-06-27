# Contributing

Contributions to Nuneri AI Assets start with GitHub Issues.

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

Every PR must link the accepted issue, include validation output, and declare provider impact.

## Step 5 - CODEOWNERS Approval, Merge, and Distribute

CODEOWNERS approval is required before merge.

## Issue Labels and Triage States

Use type, asset, provider, priority, and status labels from `.github/labels.yml`.

## Issue to Release Flow

Accepted issues are assigned a release target and must be referenced in `CHANGELOG.md` before release.

## Release Participation

Release owner: yamini.sk@suranku.com.

## Provider Adapter Guidelines

Change canonical assets first. Adapter outputs are generated.

## Asset Frontmatter Reference

Required fields are `name`, `description`, and `category` where applicable.

## Questions

Open an issue using the feedback template.

Note: GitHub issue templates only become visible after `.github/ISSUE_TEMPLATE/` is merged to the default branch.
