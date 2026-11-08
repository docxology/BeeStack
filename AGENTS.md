# AGENTS.md - BeeStack

This project follows the research-template pattern:

1. `src/beestack/` contains side-effect-free domain computation. Sanctioned I/O
   adapters are explicit: `brain/empirical_fetch.py` performs guarded curated
   acquisition; `visualization/` and `body/flybody_scene_signpost.py` write
   presentation artifacts only when invoked by scripts. Do not introduce network
   access or printing into computational modules.
   `project_config.py` is the shared canonical configuration-read adapter; callers
   must not reintroduce the removed `pipeline.load_config` entrypoint.
2. `scripts/` contains thin orchestrators. Scripts may read config, write
   output artifacts, and call plotting or manuscript hydration helpers.
3. `tests/` uses real computations only. Do not use mocks for domain behavior.
4. `docs/manuscript/` is canonical prose. Numeric values that depend on code or
   config should use `{{VARIABLE}}` tokens hydrated by
   `scripts/z_generate_manuscript_variables.py`.
5. Use `uv` for environment and dependency management.

6. Documentation and signposting are code contracts. When changing methods,
   outputs, or fidelity language, update the nearest `README.md` and
   `AGENTS.md`, then run the signposting and documentation audit gates.
7. Empirical BeeBrain analysis is network/data gated. If public payloads are
   absent, document the availability state and blockers; do not synthesize fake
   empirical traces to make reports look complete.
   Unobserved empirical means must not be filled with zero; finite diagnostic
   maps omit them while preserving actual measured zeros.
   An unavailable current aggregate uses `analysis_unavailable`, not proof that
   standalone payloads are absent; confidence must not stand in for presence.
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
    Every supported Markdown image format requires matching sidecar provenance;
    audit and render sealing must share the same resolved image dependencies.
    Interactive HTML carries escaped, informative document titles; CDN-dependent
    viewers must not be advertised as fully offline artifacts.
11. Security posture is a code contract. Curated empirical fetch URLs must pass
    `beestack.security.validate_download_url`; zip ingest must call
    `assert_safe_zip_member`; threat model and `docs/security_posture.md` must
    stay present; run `uv run python scripts/run_security_audit.py` before release.
12. Release validation uses `scripts/audit_publication_readiness.py` (also invoked
    by `verify_generated_reports.py`). Blockers include aligned versions, a real
    source/data/figure-bound combined PDF, all 18 hydrated sections, security and
    generated audits, and `CHANGELOG.md`. Empty DOI, unavailable empirical analysis
    and below-target parseability remain explicit warnings; `--require-doi` blocks
    a DOI-less deposit. Never reuse an older version DOI.
13. Runtime authority is `.python-version` (Python 3.12.16); supported Python is
    >=3.11,<3.13 because pinned FlyBody requires NumPy 1.26.4. Vault's management
    Python is unrelated. Use `uv sync --locked --all-extras` for development gates.
14. `Observation.heading_deg` is full-bearing degrees; angular velocity is rad/s.
    Missing empirical conditions remain null with counts, not zero. Complete grids
    and explicit shared sampling rates are required for executable templates.
    Current evidence must match raw payload, configuration and implementation hashes;
    skipped/failed analysis cannot revive historical output as a current measurement.
    An absent template bank makes integrated alignment unavailable, not zero;
    preserve null through records, summaries, sweeps and raw plot data. Scientific
    charts must not compare unlike native units on shared axes or label configured
    self-tests as biological validation.
    Waggle support metadata must distinguish paired feature/binned observations,
    per-channel values and actual frames. Undefined correlations stay null;
    bounded model confidence must not clip the reported signed error improvement.
    Derived observations must remain finite or fail explicitly; do not serialize
    infinities, reclip valid degradation, or invent a methods-telemetry point for an empty run.
15. Render the manuscript locally with `scripts/render_manuscript.py`; Pandoc and
    XeLaTeX are required. No template-root commands or sibling output writes.
16. Declared `stack_contracts` are not executed-edge coverage. The current reduced
    driver uses a fixed synthetic dance, does not pass BrainState to policy or
    niche context to Body, and does not retask agents from recruitment matches.
    Counts of repeated per-tick matches are not unique recruited bees. Describe
    actual dispatch and separate scripted scenes without inventing feedback.

The upstream instruction asked agents to read `skills/PAI/SKILL.md`. If that
path is absent in this project checkout, use the installed PAI skill from the
configured Codex skill roots and preserve its practical constraints: explicit
criteria, specificity, implementation, and verification.

Before finishing changes, run:

```bash
uv lock --check
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv run pytest --cov=src --cov-report=term-missing
uv run python scripts/fetch_empirical_bee_data.py --metadata-only
uv run python scripts/analyze_empirical_bee_data.py
uv run python scripts/analysis_pipeline.py
uv run python scripts/generate_animations.py
uv run python scripts/verify_bee_render.py
uv run python scripts/review_stack_integrity.py
uv run python scripts/run_research_suite.py --assemble-only
uv run python scripts/run_methods_analysis.py
uv run python scripts/run_stack_synthesis.py
uv run python scripts/assess_digital_twin_readiness.py
uv run python scripts/z_generate_manuscript_variables.py
uv run python scripts/render_manuscript.py
uv run python scripts/signpost_project_tree.py
uv run python scripts/audit_documentation.py
uv run python scripts/run_security_audit.py
uv run python scripts/signpost_project_tree.py --check
uv run python scripts/z_generate_manuscript_variables.py
uv run python scripts/render_manuscript.py
uv run python scripts/verify_generated_reports.py
uv run python scripts/audit_publication_readiness.py --check
uv run python scripts/audit_publication_readiness.py --check --require-doi
```

Historical maintainability evidence: [`ISA.md`](ISA.md), section J, and
[`output/reports/thermo_nuclear_code_quality_review.md`](output/reports/thermo_nuclear_code_quality_review.md)
record the May 2026 review. Those PASS/count statements are not current runtime
or release evidence; use the current source-bound release receipt.
