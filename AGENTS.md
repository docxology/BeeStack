# AGENTS.md - BeeStack

This project follows the research-template pattern:

1. `src/beestack/` contains pure domain logic. Do not import infrastructure,
   write files, print, or perform network access from source modules.
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
uv run python scripts/signpost_project_tree.py --check
uv run python scripts/z_generate_manuscript_variables.py
```
