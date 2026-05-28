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
- Paoli Dryad calcium archive (`[@paoli2024dryad]`) is downloaded and parsed as a
  citation anchor, but not yet wired as a model input or held-out validation target
  (its contribution is evidentiary, not integrative).
- `overall_validation_fraction` is a config-band module self-test rate, not a
  biological-validation score; it is reported alongside the catalogued open-gap count.

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

### Pre-publication RedTeam remediation (2026-05-27, ISA iteration 10)

Eight-vector adversarial pass found defects invisible to the green oracle:

- Abstract reframed: `RESEARCH_VALIDATION_FRACTION` now presented as a config-band
  module self-test rate co-located with the open-gap count, not a bare
  "validation fraction of 1.000"; binding guard added in
  `tests/test_research_headline_honesty.py`.
- Central-complex methods prose corrected to "sky-compass bearing and optic-flow
  drift" (matches `central_complex.heading_ring`; no inertial cue is implemented).
- BeeSwarm caste list corrected to nurse/forager/guard/scout/wax-builder (matches
  `config.Caste`); the prior "builder, fanner" wording was a prose-only error.
- Stale calcium narrative in abstract/results/roadmap updated to reflect the
  downloaded-and-parsed citation-anchor state (gap count is 0).
- Two cited DOIs corrected against Crossref/PubMed: `landuse2024nutrition`
  (J. Environ. Manage., `10.1016/j.jenvman.2024.120031`) and
  `scitotenv2024varroameta` (2025, `10.1016/j.scitotenv.2024.178228`).
- Determinism hardening: `waggle_literature_regression` JSON writer now uses
  `sort_keys=True`; `swarm/agents.py` caste selection uses a `(prob, name)`
  tie-break (matches the policy convention).
- Removed two checkout-specific absolute paths from shipped docs.
