# AGENTS.md - BeeStack

This project follows the research-template pattern:

1. `src/beestack/` contains domain logic. Do not import infrastructure,
   print, or perform network access from source modules. Pure computation
   stays side-effect free; sanctioned presentation adapters in
   `visualization/` and `body/flybody_scene_signpost.py` may write figures,
   MJCF, GIF, and signpost files when invoked from scripts.
2. `scripts/` contains thin orchestrators. Scripts may read config, write
   output artifacts, and call plotting or manuscript hydration helpers.
3. `tests/` uses real computations only. Do not use mocks for domain behavior.
4. `manuscript/` is canonical prose. Numeric values that depend on code or
   config should use `{{VARIABLE}}` tokens hydrated by
   `scripts/z_generate_manuscript_variables.py`.
5. Use `uv` for environment and dependency management.

6. Documentation and signposting are code contracts. When changing methods,
   outputs, or fidelity language, update the nearest `README.md` and
   `AGENTS.md`, then run the signposting and documentation audit gates.
7. Empirical BeeBrain analysis is network/data gated. If public payloads are
   absent, document the availability state and blockers; do not synthesize fake
   empirical traces to make reports look complete.
8. Digital-twin wording must stay conservative until longitudinal assimilation,
   held-out validation residuals, uncertainty, and governance artifacts exist.
9. Source evidence is an offline contract. Manuscript citations must use Pandoc
   bracket syntax, required BibTeX entries must carry verified DOI/source URLs,
   generated methods links must include citation keys, source DOIs, artifact
   kind, claim tier, and availability status, and Perplexity/web discovery must
   not replace directly verified scholarly or official sources.
10. Manuscript figures are evidence artifacts. Figure sidecars must preserve
    caption, alt text, manuscript section, label, claim tier, fidelity tier,
    source data, regeneration command, and unsupported-inference language; the
    hydrated manuscript must reference only existing generated images with
    sidecars. Generated project-local artifact paths should serialize as stable
    `output/...` paths, not checkout-specific absolute paths.
11. Security posture is a code contract. Curated empirical fetch URLs must pass
    `beestack.security.validate_download_url`; zip ingest must call
    `assert_safe_zip_member`; threat model and `docs/security_posture.md` must
    stay present; run `uv run python scripts/run_security_audit.py` before release.
12. Release 1.0 uses `scripts/audit_publication_readiness.py` (also invoked from
    `verify_generated_reports.py`). Blockers: aligned version strings, combined
    PDF, hydrated variables, security/generated audits, `CHANGELOG.md`. Warnings:
    empty DOI, parseable fraction below target.

The upstream instruction asked agents to read `skills/PAI/SKILL.md`. If that
path is absent in this project checkout, use the installed PAI skill from the
configured Codex skill roots and preserve its practical constraints: explicit
criteria, specificity, implementation, and verification.

Before finishing changes, run:

```bash
uv lock --check
uv run ruff check src tests scripts
uv run pytest --cov=src --cov-report=term-missing
uv run python scripts/analysis_pipeline.py
uv run python scripts/verify_generated_reports.py
uv run python scripts/audit_documentation.py
uv run python scripts/run_security_audit.py
uv run python scripts/signpost_project_tree.py --check
uv run python scripts/z_generate_manuscript_variables.py
uv run python scripts/audit_publication_readiness.py --check
```

Structural maintainability (thermo-nuclear bar) is tracked in [`ISA.md`](ISA.md)
section J (ISC-105..112). Post-remediation (2026-05-25): **119/119** criteria
pass; report
[`output/reports/thermo_nuclear_code_quality_review.md`](output/reports/thermo_nuclear_code_quality_review.md)
verdict **PASS**. ISC-65/66 are closed.
