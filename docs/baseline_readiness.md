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

- **Source-layer I/O (resolved by articulation, optional cleanup remains).**
  The architectural invariant is *scientific-domain-kernel purity*: brain,
  mind, swarm, niche, research, contracts, config, utils, orchestrator,
  manifest, integrity, manuscript_variables, and documentation_audit perform
  **zero** file writes, prints, or network I/O (grep-verified). The modules
  that do write — the visualization figure layer and the `bee_mjcf` /
  `flybody_scene` FlyBody adapters — are presentation/integration adapters
  whose external consumers (matplotlib output files, FlyBody `walker_xml_path`,
  MuJoCo) require filesystem artifacts; `AGENTS.md` rule 2 explicitly has the
  thin `scripts/` orchestrators call these helpers. So this is the intended
  design, not a violation. Pipeline regen is deterministic (24 steps / 12
  figures / 9 animations reproducible). Optional future cleanup (not a
  correctness or reproducibility need): a pure XML-string builder seam in
  `bee_mjcf` for unit-testing the MJCF mutation independent of disk.

