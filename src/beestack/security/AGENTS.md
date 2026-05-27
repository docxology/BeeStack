# AGENTS.md — `src/beestack/security/`

Security helpers for BeeStack. Domain simulation code must not import network
clients; only `beestack.brain.empirical_fetch` performs HTTPS fetches, and it
must call `validate_download_url` before every request.

## Public API

- `validate_download_url(url, *, context="")` — raises `ValueError` off allowlist
- `safe_relative_path`, `assert_safe_zip_member`, `resolve_under_root`
- `audit_security_posture(project_root)` → `SecurityPostureAudit`
- `security_posture_markdown(audit)` — report text for `output/reports/`

## Editing rules

1. Extend `ALLOWED_DOWNLOAD_HOST_SUFFIXES` only when a new **curated** public
   host is added to `brain/datasets.py` with manuscript provenance.
2. Keep posture scans free of false positives (exclude this package from pattern
   self-match).
3. Update `BeeStack-threat-model.md` and `docs/security_posture.md` when threat
   boundaries change.
