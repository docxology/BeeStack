# output/data

Generated JSON payloads, manifests, empirical analysis, and sensitivity data.

- Scope: Regeneratable output artifacts.
- Regenerate: uv run python scripts/analysis_pipeline.py
- Canonical source: BeeStack scripts and source helpers

Core JSON artifacts are produced by the offline analysis and research scripts.
Network-gated empirical JSON appears only after public payloads have been
downloaded and parsed; absent empirical JSON should be treated as a data
availability state, not as missing synthetic data.
