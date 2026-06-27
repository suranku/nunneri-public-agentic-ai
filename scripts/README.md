# scripts

This directory is part of the Nunneri AI Assets repository.

## Release Packaging

- `package_release.py` builds versioned internal release archives under `dist/releases/`.
- `check_release_package.py` verifies the archives contain installer payloads, generated provider outputs, LangGraph runtime exports, reference docs, and consumer examples.

Run both from a `release/vX.Y.Z` branch before tagging:

```bash
python3 scripts/package_release.py
python3 scripts/check_release_package.py
```
