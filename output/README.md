# Output

Regeneratable BeeStack artifacts. Run:

```bash
uv run python scripts/analysis_pipeline.py
uv run python scripts/generate_animations.py
uv run python scripts/fetch_empirical_bee_data.py
uv run python scripts/analyze_empirical_bee_data.py
uv run python scripts/run_research_suite.py
uv run python scripts/signpost_project_tree.py --check
uv run python scripts/audit_documentation.py
uv run python scripts/z_generate_manuscript_variables.py
```

Subdirectories contain data, figures, reports, interactive HTML, strict FlyBody
scene assets, and hydrated manuscript sources. Animations are written under
`output/animations/`; strict BeeSwarm MuJoCo scene XMLs and contact reports live
under `output/animations/flybody_scenes/`. Research-suite figures live under
`output/figures/research/`; optional Plotly views live under
`output/interactive/`. Raw empirical downloads live under
`output/data/empirical_sources/` and are not package source.
Every non-cache output directory, including raw asset and dataset leaves, is
signposted with local `README.md` and `AGENTS.md` files by
`scripts/signpost_project_tree.py`.
