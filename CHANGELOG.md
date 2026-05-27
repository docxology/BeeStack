# Changelog

All notable changes to BeeStack are documented in this file.

## [1.0.0] — 2026-05-25

First publication-ready manuscript and package release.

### Added

- FlyBody render still contact sheets and expanded body–swarm figure registry.
- Security module (`beestack.security`): HTTPS host allowlist, zip-slip guards, static posture audit.
- `BeeStack-threat-model.md`, `docs/security_posture.md`, and `scripts/run_security_audit.py`.
- `scripts/audit_publication_readiness.py` and `output/reports/publication_readiness.json` gate.
- Narrow PDF geometry (`margin=0.15in`) for combined manuscript output.

### Changed

- Manuscript methods, validation, ethics/governance, and discussion prose expanded.
- Figure audit handles `{#fig:… width=…}` captions and excludes meta docs from caption scans.
- Parseability readiness requires `parseable_fraction >= target` (source-verified alone no longer bypasses).

### Known gaps (documented, not hidden)

- `publication.doi` must be minted at Zenodo before public deposit.
- Paoli Dryad calcium archive (`[@paoli2024dryad]`) not yet local/parseable (Dryad 405/401 on bulk fetch).
- Brain-data parseable-source fraction below the 0.8 target until calcium payloads ingest.
- Research readiness reports list open synthesis and validation follow-ups alongside `validation_fraction=1.0`.

### Verification

```bash
uv run pytest --cov=src --cov-fail-under=90
uv run python scripts/analysis_pipeline.py
uv run python scripts/verify_generated_reports.py
uv run python scripts/audit_publication_readiness.py --check
```

### Post-release hardening (2026-05-25)

- Post-redirect HTTPS host re-validation in `empirical_fetch` (TM-002).
- Zip archive member-count and uncompressed-size caps in ingest paths (TM-003).
- Empirical analysis wired into `analysis_pipeline.py` before methods outputs.
