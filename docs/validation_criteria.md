# Validation Criteria

BeeStack uses deterministic unit tests, script-level integration tests, visual
checks, and generated audits. The goal is traceable improvement without
overclaiming fidelity.

## Code Quality

```bash
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv lock --check
uv run pytest --cov=src --cov-report=term-missing
```

Coverage over `src/` must remain at or above 92%.

## BeeBody

- Production animation paths use FlyBody tasks:
  `WalkImitation`, `FlightImitationWBPG`, `WingBeatPatternGenerator`,
  `walker_xml_path`, and `rollout_and_render`.
- Generated MJCF includes bee-specific cues: fuller banded abdomen, four
  translucent wings, hamuli/hindwing coupling, compound eyes, antennae,
  proboscis, mandibles, thorax fuzz, stinger, and pollen baskets.
- Body calibration reports honeybee mass, abdomen/thorax proportion,
  four-wing/hindwing-coupling, contact-proxy, and inertia-rescaling witnesses;
  morphology score must remain at or above 0.85.
- `scripts/verify_bee_render.py` checks walk and flight GIFs, contact sheets,
  silhouette score, bee-specific cues, motion, and absence of debug aids.

## BeeSwarm Strict FlyBody Scenes

- `beeswarm_10_beebody_collision.gif`,
  `beeswarm_waggle_dance_configured.gif`, and
  `beeswarm_waggle_dance_long.gif` are production FlyBody-generated BeeBody
  MJCF scenes rendered through MuJoCo, not Matplotlib glyphs.
- The collision scene must contain the configured bee count, unique prefixed
  bodies/free joints/actuators, hidden contact proxy geoms, and at least the
  configured number of actual bee-bee contact pairs.
- Each waggle scene must contain one dancer plus configured followers, a
  comb/floor arena, decoded waggle-path settings, and finite floor/body contact
  metrics.
- Waggle scene contact reports must include finite follower distance,
  follower-orientation error, follower-orientation confidence, and waggle-phase
  samples.
- Configured waggle scenes must keep mean follower orientation error below
  35 degrees and follower orientation confidence above 0.65.
- `scripts/verify_bee_render.py` checks the swarm GIFs, scene XMLs, render
  backend strings, contact reports, and nonblank/dynamic frames.

## BeeBrain

- Dataset registry entries include DOI/source URL, modality, module target,
  variables, sample, integration target, and license note.
- Anatomy parsers handle FU Berlin ZIP inventories, TIFF/JPG stack metadata,
  VRML geometry summaries, and neuropil abbreviation tables.
- Activity parsers handle Paoli `.mat`, Carcaud/Andreu/Nouvian workbooks, and
  Jernigan CSV movement summaries when local payloads are available.
- Waggle follower parsers handle the CC BY 4.0 Hadjitofi-Webb Figshare CSVs:
  per-frame features, binned antenna features, model error tables, reduced
  error summaries, and orientation straightness rows.
- `BeeBrainActivitySummary` reports odor separability, calcium latency,
  inhibitory/excitatory fraction, aftersmell response, region response means,
  antennal active-sensing drive, waggle follower confidence, and
  neuromodulatory defence summaries.
- `BeeBrainDataCompletenessPanel` reports downloaded and parseable fractions,
  modality counts, module-target counts, a module/modality matrix, and explicit
  source gaps.
- `brain_data_parseable_fraction` must satisfy the configured empirical
  completeness threshold (`0.5` in `manuscript/config.yaml`). The stricter
  `0.800` parseability target remains an improvement target. Remaining blockers
  are allowed only when every curated source is DOI/source-verified and the blocker,
  parser status, and remediation path are recorded.

## Mind, Swarm, Niche

- BeeMind policy selection diagnostics include selected policy, competing
  policies, energy/risk terms, belief deltas, and colony-need inputs.
- BeeSwarm outputs reduced dance recruitment, pheromone gradients, task
  allocation, BEEHAVE-compatible colony summary fields, and separate strict
  FlyBody/MuJoCo production scenes for waggle/collision visualization.
- BeeSwarm waggle recruitment diagnostics include empirical follower confidence,
  follower-alignment score, stop-signal factor, colony food need, and per-agent
  probabilities.
- BeeNiche outputs comb occupancy, thermal metrics, foraging-environment
  metrics, and Hiveopolis/BEEHAVE-compatible adapter schemas.
- Calibrated BeeNiche brood-temperature error should remain below 3 degrees C
  in generated methods and research reports.

## Research Suite

```bash
uv run python scripts/review_stack_integrity.py
uv run python scripts/run_research_suite.py --assemble-only
uv run python scripts/run_methods_analysis.py
uv run python scripts/run_stack_synthesis.py
uv run python scripts/verify_generated_reports.py
```

- `ResearchSuiteReport` must include five module scorecards, visualization
  records, empirical registry/evidence rows, evidence availability states,
  sensitivity sweeps, and known gaps.
- Empirical evidence rows must use one of `parsed`, `generated`,
  `registered_absent`, `network_gated_absent`, or `missing_optional`; rows with
  absent availability states must not be rendered as current manuscript support.
- Scorecard metrics and sensitivity outputs must be finite, typed, JSON
  serializable, and deterministic from a fixed config/seed.
- Research figures under `output/figures/research/` must be nonblank, and
  Plotly HTML outputs under `output/interactive/` must contain data traces.
- The report must preserve fidelity labels: strict FlyBody/MuJoCo for Body and
  Swarm production animations, empirical reduced for BeeBrain, and reduced
  validated kernels for Mind, non-visual Swarm dynamics, and Niche.
- `MethodsAnalysisReport` must include five module methods panels, validation
  panels, visualization panels, scenario sweep panels, evidence availability
  links, a source-claim crosswalk, finite quantitative metrics, and top
  validation gaps.
- Every methods manuscript evidence link must preserve `citation_keys`,
  `source_dois`, `artifact_kind`, `claim_tier`, and `availability_status`.
- `scripts/verify_generated_reports.py` must pass with no stale
  local test-result reports, no missing `parsed`/`generated` evidence artifact,
  no failed synthesis gate that still uses success wording, and no project-root
  absolute paths in generated JSON/Markdown under `output/data` or
  `output/reports`.
- Methods figures under `output/figures/methods/` must be nonblank, and Plotly
  methods HTML outputs under `output/interactive/` must contain traces.
- Figure sidecars must preserve caption, alt text, manuscript section, Pandoc
  figure label, claim tier, unsupported-inference boundary, validation status,
  source data, regeneration command, accessibility checks, and optional
  figure-design citation metadata.
- The figure audit must pass: hydrated manuscript image paths must resolve,
  labels must be unique, captions must be nonempty, PNG sidecars must exist,
  curated high-priority figures must be inserted, and gap/absent figures must
  not be captioned as positive support. Sidecar labels/captions must agree with
  hydrated manuscript callouts, primary manuscript captions must name backend,
  source data, validation, and conservative interpretation, and generated
  project-local paths must not leak checkout-specific absolute prefixes.
- `StackSynthesisReview` must include five module synthesis panels, finite
  simulation telemetry statistics, artifact/signposting/scholarship gates, and
  a nonblank `output/figures/research/stack_synthesis_dashboard.png` figure.

## Documentation And Manuscript

```bash
uv run python scripts/audit_documentation.py
uv run python scripts/z_generate_manuscript_variables.py
```

The documentation audit checks command references, source links, generated
output paths, fidelity language, unresolved manuscript variables, Pandoc
citation keys, required BibTeX DOI/source URL metadata, bibliography coverage
for dataset-registry DOIs, manuscript figure references, figure sidecars,
curated figure insertion, and conservative digital-twin wording. The manuscript
generation step must leave no unresolved `{{TOKEN}}` variables in
`output/manuscript/`.

## External Research And Digital-Twin Boundaries

- README and module docs must distinguish current evidence tiers from the
  long-term digital-twin target. BeeStack is a scaffold until longitudinal
  assimilation, held-out forecast skill, residual reporting, and governance
  artifacts are implemented.
- Any claim about FlyBody/MuJoCo fidelity must name the exact generated scene,
  renderer/backend, contact or visual signature check, and failure mode when
  strict dependencies are absent.
- Any claim about waggle-following or antennal-position evidence must name the
  public source, parser, generated summary, and confidence/error metric.
- Hadjitofi-Webb evidence supports follower antennal-positioning and
  decoding-error diagnostics; it does not validate colony-scale recruitment.
- Any BEEHAVE, Hiveopolis, colony-demography, or population-of-colonies claim
  must be framed as adapter/readiness work unless validated against external
  scenario tables or longitudinal observations.
- Any external-source refresh that materially changes scope or methods language
  should leave a note under `output/llm/` or an equivalent report artifact with
  source URLs, date, command, and affected documentation paths.
