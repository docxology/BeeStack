# Research Suite Results

The research suite is BeeStack's *cross-module evidence consolidator*.
It assembles fidelity-labelled scorecards, empirical-evidence rows,
visualization-artifact inventories, deterministic sensitivity sweeps,
and a known-gaps catalogue, then writes a primary research report and
a methods-analysis pass.

## Research-suite report

The research suite writes
`output/reports/beestack_research_report.md`,
`output/reports/beestack_research_report.json`, and
`output/data/research_suite_report.json`. It reports five module
scorecards, {{RESEARCH_EVIDENCE_COUNT}} empirical evidence records,
{{RESEARCH_VISUALIZATION_COUNT}} visualization artifacts,
{{RESEARCH_SWEEP_COUNT}} deterministic sensitivity sweeps, and
{{RESEARCH_KNOWN_GAP_COUNT}} known gaps. The overall validation
fraction is {{RESEARCH_VALIDATION_FRACTION}}.

![BeeStack research scorecard heatmap](../figures/research/research_module_scorecard_heatmap.png){#fig:research_scorecard}

![BeeStack sensitivity sweeps](../figures/research/research_sensitivity_sweeps.png){#fig:research_sweeps}

![BeeStack fidelity and evidence network](../figures/research/research_fidelity_evidence_network.png){#fig:research_network}

## Stack-synthesis review

The cross-stack synthesis review is a stricter summary layer over the
research report, methods-analysis report, simulation records, animation
manifest, documentation audit, readiness review, and bibliography. It
writes `output/reports/stack_synthesis_review.md`,
`output/reports/stack_synthesis_review.json`, and
`output/data/stack_synthesis_review.json`, plus
{{STACK_SYNTHESIS_FIGURE_COUNT}} figure(s) including
`output/figures/research/stack_synthesis_dashboard.png`.

The latest synthesis reports validation fraction
{{STACK_SYNTHESIS_VALIDATION_FRACTION}}, synthesized readiness fraction
{{STACK_SYNTHESIS_READINESS_FRACTION}}, artifact coverage
{{STACK_SYNTHESIS_ARTIFACT_COVERAGE}}, and
{{STACK_SYNTHESIS_SCHOLARSHIP_REF_COUNT}} bibliography anchors. The
integrated run improved brood-temperature error by
{{STACK_SYNTHESIS_THERMAL_IMPROVEMENT_C}} \si{\degreeCelsius}. The top
synthesis finding is: **{{STACK_SYNTHESIS_TOP_FINDING}}**

![BeeStack cross-stack synthesis dashboard](../figures/research/stack_synthesis_dashboard.png){#fig:stack_synthesis_dashboard}

## Module scorecards

The scorecards make fidelity labels first-class.

- **BeeBody** is FlyBody-backed for rendering plus a reduced
  closed-loop telemetry kernel.
- **BeeBrain** is an empirical reduced neural kernel — empirical at
  the data surface, reduced at the dynamics surface.
- **BeeMind** is a bounded active-inference-style policy kernel
  [@friston2010free; @parr2017working] with explicit diagnostics.
- **BeeSwarm** combines strict FlyBody/MuJoCo visual scenes
  [@vaxenburg2025flybody; @todorov2012mujoco] with a reduced
  communication kernel.
- **BeeNiche** is a voxel comb and thermal kernel with BEEHAVE and
  Hiveopolis adapter schemas [@becher2014beehave;
  @narsicht2020hiveopolis].

Each module also exposes contract coverage, validation pass count,
empirical-evidence count, and known-gap count, so the heatmap row for
a module is interpretable without the surrounding prose.

## Sensitivity sweeps

The sensitivity sweeps are deterministic: each sweep varies a single
configuration knob over a fixed grid, records the resulting BeeStack
diagnostics, and serializes the result to
`output/data/sensitivity/<knob>.json`. The default sweep size is 5
samples per knob, which is the smallest grid that produces a visible
monotone signal on every recorded diagnostic without inflating CI
wall-time. The sweeps are *not* a substitute for a Bayesian
calibration; they are a *contract-stability witness* that says: when
the kernel is asked to change one parameter at a time, the
intermediate states and final outputs respond consistently and within
configured bounds.

This follows the spirit of global sensitivity analysis: the first goal
is not to claim calibrated predictive uncertainty, but to expose which
outputs move under controlled parameter changes and which outputs are
structurally insensitive under the current reduced kernel
[@saltelli2008global].

## Readiness review

The readiness review writes
`output/reports/project_readiness_review.md` and
`output/reports/project_readiness_review.json`. It currently reports
strict signposting coverage for {{SIGNPOSTED_DIRECTORY_COUNT}}
directories and keeps the next-improvement backlog tied to the
research-suite gaps. The top prioritized improvement is
**{{READINESS_TOP_PRIORITY}}**.

The readiness review is structurally different from the
research-suite report. The research-suite report describes *current
state*; the readiness review describes *recommended next state*.
Keeping the two separated avoids a common failure mode in research
software, where forward-looking optimism leaks into descriptive
artifacts and slowly displaces honest gap reporting.

## Methods-analysis pass

The methods-analysis report writes
`output/reports/methods_analysis.md`,
`output/data/methods_analysis.json`,
`output/reports/manuscript_figure_index.md`, and
`output/data/manuscript_figure_index.json`. It reports
{{METHODS_PANEL_COUNT}} module methods panels,
{{METHODS_SWEEP_PANEL_COUNT}} scenario-sweep panels,
{{METHODS_VISUALIZATION_COUNT}} linked visualization records, and an
overall methods validation fraction of {{METHODS_VALIDATION_FRACTION}}.
Its `all_validations_passed` flag is {{METHODS_ALL_VALIDATIONS_PASSED}},
and its highest-priority visible gap is **{{METHODS_TOP_GAP}}**.

## What "validation fraction" means

A validation fraction is the share of *registered checks* that
currently pass. It is not a model-quality score, and it is not a
biological-realism score. A fraction of 1.0 means: every check that
the project has decided to run, currently passes. Increasing the
denominator (adding stricter checks) can lower the fraction; that is
a feature, not a bug, because it makes the bar visible.

## Reading the scorecards

To audit a single number in this section:

1. Open the linked JSON report
   (e.g. `output/reports/beestack_research_report.json`).
2. Find the module of interest.
3. Read the `validation` list to see which checks ran and which
   passed.
4. Cross-reference any failed check against the `known_gaps` list
   in the same report.

Every JSON report in the suite is small enough to read directly; that
is intentional. A reproducible-research artifact that requires
specialized tooling to inspect is one that drifts silently from the
prose that describes it [@wilson2017good].

## How the reports divide responsibility

The report set is intentionally redundant only at the edges. The
integrity review answers "what API and contract does each module
expose?" The methods-analysis report answers "what method diagnostics,
figures, and validation panels exist for each module?" The research
suite answers "what is the cross-module evidence state?" The
stack-synthesis review answers "what do the generated statistics imply
across all of those surfaces?" The readiness review answers "what should
improve next?" The documentation audit answers "does the prose still
point to artifacts that exist?" Keeping those questions separate
prevents a single large report from becoming a place where
implementation detail, scientific evidence, roadmap intent, and
documentation health blur together.
