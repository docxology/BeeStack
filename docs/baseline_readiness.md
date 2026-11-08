# Baseline Readiness Note

BeeStack's next-sprint baseline is a Full Snapshot research-operations state:
source, tests, docs, manuscript, configs, generated reports, figures,
animations, manifests, and lightweight JSON/Markdown outputs are intended to be
reviewable in git. Raw empirical archives and large third-party payloads under
`output/data/empirical_sources/` remain script-regeneratable caches.

Current readiness targets:

- Source coverage gate: `pytest --cov=src` at or above 92%.
- BeeBrain empirical gate: `brain_data_parseable_fraction >= 0.5` in this
  checkout, plus DOI/source verification, parser status, and remediation for
  every remaining blocker. The stricter `0.800` target remains an improvement
  target.
- BeeBody calibration gate: morphology calibration score at or above 0.85.
- BeeSwarm waggle gate: mean follower orientation error below 35 degrees and
  orientation confidence above 0.65.
- BeeNiche reduced-kernel thermal self-test target: brood-temperature error below 3 degrees C, not biological calibration.
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

- **Domain computation and explicit adapters.** Domain kernels remain pure;
  guarded empirical acquisition and FlyBody/visualization presentation adapters
  perform bounded I/O when invoked by orchestration. See `architecture.md` and
  `security_posture.md`; source-wide purity claims are not appropriate.
- **Current evidence versus retained snapshots.** Readiness requires current
  source-bound reports and scoped runtime receipts. Historical step, figure,
  animation, or PASS counts are not a new reproducibility result.
- **Biological calibration.** Morphology cues, contact metrics, configured thermal
  bands, and deterministic replay are engineering witnesses. Assimilation,
  held-out residuals, uncertainty, and governance remain the twin-readiness bar.

