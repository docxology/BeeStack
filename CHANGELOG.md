# Changelog

All notable changes to BeeStack are documented in this file.

## [2.0.0] — unreleased candidate

### Breaking contracts

- Required full-bearing `Observation.heading_deg` (degrees) and model-owned fixed
  `SimulationState.kenyon_projection`; angular velocity remains radians/second.
- Missing empirical error/antenna conditions are null with observation counts,
  not zero error or fictitious confidence. Reports and recruitment preserve missingness.
- State-based adapter stepping is explicitly reduced; strict requests cannot be
  mislabeled as FlyBody physics. Strict environment/render paths remain separate.
- Python >=3.11,<3.13, pinned development runtime 3.12.16, and exact FlyBody commit.
- Download caches require verified completion records; arbitrary Lambda/AWS targets
  are not curated origins. Container/array budgets apply before expansion/allocation.
- No implicit synthetic template bank: absent alignment remains null. Scenario
  panels retain nullable observations and derived counts/ranges; incomplete series
  are unavailable, and the cross-unit `dominant_output` ranking is removed.
- Optional activity/antenna measurements and an empty quality conjunction stay
  null with contributing counts. Undefined zero-norm odor cosine pairs do not
  contribute observations; measured zero statistics remain zero.
- Sparse waggle records retain null angle/frame/straightness measurements and
  undefined correlations, with per-statistic support and feature/binned source.
  The reported error-improvement ratio is not clipped when error more than doubles;
  neutral model-drive fallbacks remain distinct from measured values.
- Figure data use native-value tables and independent axes instead of mixed-unit
  normalization, remapped correlations, or unrelated angles on a shared polar plot.
  Research provenance now uses the `research_evidence_inventory` claim tier.
- Evidence availability adds `analysis_unavailable` when no current aggregate is
  supplied. Represented counts/parseability no longer imply standalone payload
  absence; a parsed waggle source remains present when confidence is zero.

- Executable empirical templates require complete observed grids and finite shared
  sampling rates. Source labels remain positional when biological identities are
  absent; missing values are never silently imputed. Published Wilcoxon W retains
  valid fractional ranks; annotations and figure captions are not table conditions.
- Research/methods metric maps and validation values preserve null unavailable
  observations; missing numeric checks fail without disappearing from denominators.
  Hydrated numeric counts require nonnegative whole numbers, not boolean/fractional
  substitutes. Public token names remain unchanged.
- GIF FPS is integer 1..100. Native/Matplotlib paths share one encoder; the
  Matplotlib backend is `matplotlib.savefig+Pillow`. `ArrayLimits` now lives in
  `brain.empirical_data`; tabular parsing accepts keyword-only `limits`. The pure
  policy model resolves through normal runtime type introspection without parser
  package cycles or compatibility re-exports.

### Corrected

- Canonical `docs/manuscript` readers, preflight hydration custody, citation/image
  discovery, real source-bound PDF readiness and installed-wheel console entrypoints.
- Numerical dimensions/finiteness, heading units, wing DOFs, sparsity ceilings,
  configured/time-aware thermal dynamics, coherent patch belief and full-twin coverage.
- Per-hop redirect admission and credential scoping, atomic bounded downloads,
  nested ZIP/XLSX/MAT/HDF5 intake, bounded VRML prefixes and asset-backed structural coverage.
- Unique evidence inventories with authoritative provenance and cwd-independent paths;
  skipped empirical stages cannot revive retained reports as current measurements.
- Configured render-verification counts/paths/thresholds and periodic motion detection.
- Manuscript claims now distinguish current availability, historical empirical figures,
  cue heuristics, configured self-tests and biological validation.
- Source-bound download completion and current-analysis/render receipts prevent
  failed refreshes or changed raw inputs/configuration/code from reviving old proof.
- Refused download locators no longer disclose credentials/query values in policy
  diagnostics or acquisition catalogs. File hashing streams bounded chunks.
- The registered publisher supplement was acquired and parsed through the actual
  loader; this is published-statistics availability, not connectivity or biological
  validation. Missing calcium/panel payloads remain explicit.
- Local Pandoc/XeLaTeX rendering, fail-closed cross-references, cold-checkout audit
  ordering, MIT license text and preserved Apache-2.0 FlyBody asset notices.
- Every supported Markdown image dependency and sidecar is sealed, including JPEG/
  vector images outside the figures folder. Figure provenance is format-independent.
- Malformed provider locators remain per-file errors even in metadata-only mode;
  following dataset/file observations are preserved.
- Offline figure admission no longer demands historical empirical plots: core
  primaries remain mandatory, current empirical primaries remain required, and
  stale empirical references fail. Canonical config reading moved cleanly to
  `beestack.project_config.load_config` to avoid an orchestration dependency cycle.
- The local compiler now resolves images from the same origin as figure admission,
  records working directories, and wraps literal provenance paths in table cells.
  Current prose/figures no longer carry obsolete implementation-version labels;
  this does not promote their scientific fidelity or calibration status.
- Signposting excludes transient `build/` and `dist/` trees, preventing generated
  folder guides from leaking into subsequently built distribution artifacts.
- Manuscript timing now separates configured policy/physics targets from the
  executed reduced loop; reproducibility claims name the three compared JSON
  artifacts rather than promising identical rendering or timestamped reports.
- Final browser review exposed shared/mixed-unit axes and an implicit synthetic
  prior fallback masquerading as empirical template alignment. Explicit supplied
  banks, nullable simulation/sweep outputs, native-unit small multiples, a module-
  metric table and configured-self-test labels close those scientific-presentation
  defects without inventing observations.
- Methods/research metrics omit unobserved odor means while retaining measured
  zero. Static and interactive module tables preserve native units.
- The graphical abstract distinguishes the executed synthetic scenario from the
  seven declared interfaces. Source-class count tables share one raw/render data
  authority; claim ceilings and readiness requirements are not execution receipts.
- Informative manuscript headings retain section IDs. Current prose no longer
  claims BrainState/niche feedback, recruitment retasking, inferred tripod gait,
  or full contract-edge execution. Partial refresh recipes defer final sealing
  to the canonical bootstrap/audit/final-hydration/render/publication order.
- Generated Matplotlib font caches are excluded from source custody without
  excluding project guidance or relaxing test-source drift checks.
- Methods telemetry images and raw exports share null/empty-series semantics;
  missing measurements no longer export as observed zeros or a synthetic first step.
- Relative-error and unit-conversion overflow fail explicitly, while streaming
  absolute-error means preserve representable results without overflowing their sums.
- Interactive viewers now expose informative, escaped browser document titles
  while retaining deterministic plot IDs and the documented Plotly CDN dependency.
- The real pipeline/hydration regression now uses an isolated temporary project
  and four-frame real renders, preserving physics, resolution and simulation steps;
  it verifies that checkout artifacts remain untouched. Full production inputs
  remain exercised by the installed-CLI CI gate.
- Removed obsolete manuscript filename/wording snapshots rather than re-pinning
  them. Native documentation, source, hydration and rendered-publication gates remain.
- CI now emits non-terminating Python stack dumps and slow-test durations without
  skipping tests, lowering coverage or increasing its existing hard bound.
- CI bounds BLAS/OpenMP/NumExpr threads to one, matching the qualified local
  verification environment rather than relying on unknown native-library defaults.
- The security guide names the canonical configuration adapter; its index and
  custody guidance distinguish regenerable analyses from retained empirical
  payloads, completion records and frozen validation/release packets.
- Native swarm scenes no longer inherit oversized cinematic offscreen buffers
  or repeat lighting/shadow passes for each copied body's studio lights. Buffers
  match the requested viewport; one scene key and the shared headlight prevent
  bee-count-dependent exposure. Native antialiasing/shadow-texture quality remain.
  Geometry, physics, dimensions and full frame/bee counts are unchanged, with an
  explicit serialized visual profile and real compiled-model/GIF regressions.
- Walking-manifest titles/captions and animation guidance now name configured
  tripod-pattern controls rather than implying a classified gait, matching the
  manuscript's explicit boundary.
- Shared cumulative GIF centisecond boundaries remove accumulated per-frame
  rounding drift, preserve coalesced exposure and close failed Matplotlib figures
  without replacing prior artifacts before successful frame capture.
- Finite scale-stable cosine/weighted aggregation and normalized bearing operands
  preserve representable results. Exact cancellation paths retain residuals that
  rounded products lose; unsupported finite results fail explicitly.
- Completeness counts use unique target datasets only. Kenyon subtype counts now
  share the sparse kernel's truncated boundary, with class fractions in [0, 1].
- Derived odor-panel allocation is budgeted before dense storage and requires
  complete support. HDF5 external raw storage and virtual layouts refuse during
  whole-file preflight, including unselected datasets.
- Missing/nonfinite report telemetry cannot become a passing zero witness. Raw
  methods PNG/data and manuscript means/counts reject boolean/nonfinite inputs;
  empty runs stay empty and actual measured zero remains observed.
- Unavailable connectome edge counts hydrate as N/A; supplied empty graphs retain
  zero. Positive KC sparsity retains meaningful precision instead of rounding to0.
- Default manuscript figure admission now requires exact curated registry paths
  and caption/label agreement even for tampered indexed metadata. Strict DOI
  admission rejects malformed/known-1.0 values without pretending to verify an
  unknown DOI's version assignment. Test-fixture claims distinguish synthetic
  controls and I/O doubles from biological observations; raw source custody is
  retained across the runbook, baseline guide and manuscript.

### Release boundaries

The historical 1.0 DOI is not reused. The current version requires a separately
assigned DOI before deposit; empirical payload availability and native-tool/runtime
verification remain explicit in the release receipt. No calibrated colony-twin claim.

### Historical candidate verification — 03ecbebb (2026-11-08)

- Python 3.12.16 on macOS arm64: 750 tests passed; combined line/branch coverage
  92.84%, with the 92% floor unchanged. Locked install, Ruff lint and format checks passed.
- Both non-editable wheel console commands ran real workflows from unrelated
  working directories. All 206 lazy exports resolved; the sdist rebuilt 119
  byte-identical packaged files. The three reduced-core JSON outputs reproduced exactly.
- Native FlyBody/MuJoCo render/contact checks and manuscript/document/security
  gates ran. The combined 56-page PDF was visually inspected, with zero missing
  glyphs and zero overfull boxes. Strict deposit admission remains blocked by the
  absent new version-specific DOI; no 2.0 tag or release has been published.
- All four HTML surfaces were exercised in installed desktop Chrome, including
  actual legend hide/restore, 24 independent visible sweep axes, three unavailable
  alignment series without plotted points, and a 49-row native-unit metric table.
  This is not cross-browser, accessibility or biological validation.
- Evidence, superseded failures, scientific limitations and unexercised surfaces:
  [Workflowz release audit](output/reports/workflowz_release_audit.json).

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
uv run pytest --cov=src --cov-fail-under=92
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
