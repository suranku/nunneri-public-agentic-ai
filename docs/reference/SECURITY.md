# Security Policy

Nunneri is public source under the AGPLv3 Community Edition with commercial licensing available. Security reports should be handled privately before public disclosure.

## Supported Versions

| Version | Support |
| --- | --- |
| `main` | Active development and validation |
| Latest `v0.x` prerelease | Best-effort security fixes |
| Older prereleases | Not supported unless explicitly stated |

## Reporting a Vulnerability

Email `core@nunneri.com` with the subject `Nunneri Security Report`.

Temporary fallback until Nunneri domain email is active: `yamini.sk@suranku.com`.

Include:

- affected version, commit, or release tag
- affected component, such as API, Graph Studio, installer, generated assets, runtime contract, or provider adapter
- reproduction steps
- expected and actual impact
- logs, screenshots, or proof-of-concept details if safe to share privately

Do not open a public GitHub issue for a suspected vulnerability until the Nunneri Core Team has reviewed it.

## Response Targets

These are targets, not guaranteed service-level commitments:

- Acknowledge report: 3 business days
- Initial triage: 7 business days
- Coordinated public disclosure: after a fix, mitigation, or documented non-issue is available

## Security Scope

In scope:

- authentication and authorization bypass
- multi-tenant isolation failures
- approval-gate bypass or unauthorized gate approval/rejection
- leakage of provider keys, API tokens, thread state, run outputs, checkpoints, or tenant data
- unsafe installer behavior
- release artifact tampering or validation bypass

Out of scope unless paired with a concrete exploit:

- generic dependency advisories with no reachable path
- denial-of-service against local development servers
- social engineering
- vulnerabilities in external services not controlled by Nunneri

## Secrets and Provider Keys

Nunneri should not require provider keys in committed files. Use environment variables, local secret managers, or deployment secret stores.

Never commit `.env`, API keys, OIDC client secrets, LangSmith keys, cloud credentials, or local database credentials.

## Disclosure Language

Nunneri publishes `ARCHITECTURE.md` and `DEFENSIVE_PUBLICATION.md` for implementation transparency and public-disclosure purposes. Do not describe Nunneri as "patent pending" unless a provisional or nonprovisional patent application has actually been filed.
