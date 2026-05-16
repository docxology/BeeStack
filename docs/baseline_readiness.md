# Baseline Readiness Note

BeeStack's next-sprint baseline is a Full Snapshot research-operations state:
source, tests, docs, manuscript, configs, generated reports, figures,
animations, manifests, and lightweight JSON/Markdown outputs are intended to be
reviewable in git. Raw empirical archives and large third-party payloads under
`output/data/empirical_sources/` remain script-regeneratable caches.

Current readiness targets:

- Source coverage gate: `pytest --cov=src` at or above 92%.
- BeeBrain empirical gate: `brain_data_parseable_fraction >= 0.800`, or every
  remaining blocker is DOI/source-verified with parser status and remediation.
- BeeBody calibration gate: morphology calibration score at or above 0.85.
- BeeSwarm waggle gate: mean follower orientation error below 35 degrees and
  orientation confidence above 0.65.
- BeeNiche thermal gate: calibrated brood-temperature error below 3 degrees C.
- Documentation gate: zero missing output references, zero unresolved
  manuscript variables, and complete README/AGENTS signposting.

The central generated evidence remains:

- `output/reports/methods_analysis.md`
- `output/reports/beestack_research_report.md`
- `output/reports/project_readiness_review.md`
- `output/reports/documentation_audit.md`
- `output/data/brain_data_completeness.json`
- `output/animations/flybody_scenes/waggle/contact_metrics.json`

## Tracked Follow-Ups

- **Source-layer I/O extraction.** `src/beestack/body/bee_mjcf.py` and
  `body/flybody_scene.py` write MJCF/scene/GIF/signpost files, and
  `brain/anatomy.py` reads archives, from within source modules — counter to
  `AGENTS.md` rule 1 ("do not write files from source modules"). This is
  deliberately deferred (not silently dropped): the heaviest offenders sit on
  the FlyBody/MuJoCo `# pragma: no cover` path, and the coverage gate margin is
  thin, so a sweeping refactor is high-risk / low-verifiability. Pipeline regen
  is empirically deterministic (24 steps / 12 figures / 9 animations
  reproducible), so the I/O-in-source is a hygiene/testability concern, not a
  reproducibility hazard. Follow-up: introduce pure XML/bytes builder functions
  in `src/` and move disk writes into `scripts/`, coverage-monitored per
  module.

