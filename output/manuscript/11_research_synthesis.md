# Research Synthesis of Evidence, Sensitivity, and Readiness {#sec:research_synthesis}

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
scorecards, 5 empirical evidence records,
75 visualization artifacts,
3 deterministic sensitivity sweeps, and
11 known gaps. The configured self-test fraction is
0.750. Native-value inventory tables, independent-axis
sensitivity sweeps, and complete evidence/gap tables come from the typed report.
Counts and configured bands are not biological validation or measured network
topology; sidecars state the unsupported inferences.

[@fig:research_scorecard] separates configured self-test fractions from native inventory counts.

![Configured self-test fractions and native metric, evidence, gap, and filename-associated artifact counts by module, without normalization or a composite score. Generated from ResearchSuiteReport scorecards and visual inventory using Matplotlib/pandas. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not support biological predictive validity.](../figures/research/research_module_scorecard_heatmap.png){#fig:research_scorecard}

[@fig:research_sweeps] plots deterministic sensitivity sweeps.

![Deterministic sensitivity-sweep panel showing reduced-kernel response under controlled one-parameter perturbations. Generated from ResearchSuiteReport sensitivity sweeps using Matplotlib/pandas. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not replace Bayesian calibration or external scenario validation.](../figures/research/research_sensitivity_sweeps.png){#fig:research_sweeps}

[@fig:research_network] summarizes reported evidence, gaps, and fidelity in a table.

![Reported module evidence and gap counts beside declared fidelity. The companion retains all source rows; no measured network topology is inferred. Generated from ResearchSuiteReport evidence records using Matplotlib/pandas. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not make empirical coverage complete.](../figures/research/research_fidelity_evidence_network.png){#fig:research_network}

[@fig:research_evidence_detail] retains all scorecard evidence/gap text and empirical source rows with availability and integration targets.

![Complete research scorecard evidence and gap text with all empirical source rows, reported availability states, and integration targets. Generated from ResearchSuiteReport evidence records and empirical availability rows using Matplotlib/pandas. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not make empirical coverage complete.](../figures/research/research_evidence_detail.png){#fig:research_evidence_detail width=98%}

## Stack-synthesis review

The cross-stack synthesis review is a stricter summary layer over the
research report, methods-analysis report, simulation records, animation
manifest, documentation audit, readiness review, and bibliography. It
writes `output/reports/stack_synthesis_review.md`,
`output/reports/stack_synthesis_review.json`, and
`output/data/stack_synthesis_review.json`, plus
2 figure(s), including
`output/figures/research/stack_synthesis_dashboard.png` and the split
findings companion.

The latest synthesis reports configured self-test fraction
0.750, heuristic readiness score
0.842, artifact coverage
1.000, and
93 bibliography anchors. These are report
diagnostics, not validated biological maturity. Digital-twin readiness remains
`False`. The signed reduced-run thermal-error change is
3.964 °C; it is not a calibrated hive response.
The top synthesis finding is: **Weakest synthesized module is BeeBrain (readiness 0.483; gaps 2).**

[@fig:stack_synthesis_dashboard] summarizes cross-stack synthesis metrics and readiness fractions.

![Configured self-tests and heuristic readiness beside native inventory counts, native-unit cross-stack statistics, and prioritized findings. Generated from output/reports/stack_synthesis_review.json using Matplotlib/pandas. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not make BeeStack digital-twin ready.](../figures/research/stack_synthesis_dashboard.png){#fig:stack_synthesis_dashboard}

[@fig:stack_synthesis_findings_detail] keeps the prioritized synthesis findings visible next to module readiness scores.

![Module heuristic-readiness scores and known-gap counts beside all prioritized cross-stack findings. These are report diagnostics, not biological validation. Generated from output/reports/stack_synthesis_review.json using Matplotlib/pandas. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not make BeeStack digital-twin ready.](../figures/research/stack_synthesis_findings_detail.png){#fig:stack_synthesis_findings_detail width=98%}

## Module scorecards and fidelity labels

The scorecards make fidelity labels first-class.

- **BeeBody** is FlyBody-backed for rendering with a separate reduced-scenario
  telemetry kernel.
- **BeeBrain** is a reduced neural kernel with availability-gated empirical data
  interfaces, not an always-populated empirical dynamics model.
- **BeeMind** is a bounded active-inference-style policy kernel
  [@friston2010free; @parr2017working] with explicit diagnostics.
- **BeeSwarm** combines strict FlyBody/MuJoCo visual scenes
  [@vaxenburg2025flybody; @todorov2012mujoco] with a reduced
  communication kernel.
- **BeeNiche** is a voxel comb and thermal kernel with BEEHAVE and
  Hiveopolis adapter schemas [@becher2014beehave;
  @hiveopolis2019project].

The inventory separates configured self-test fractions, evidence rows, known
gaps, metrics, and filename-associated artifact counts. It does not normalize
these unlike quantities into a common measurement or composite validation score.

## One-parameter reduced-kernel sensitivity sweeps

The sensitivity sweeps are deterministic: each sweep varies a single
configuration knob over a fixed grid, records the resulting BeeStack
diagnostics, and serializes the result to
`output/data/sensitivity/sensitivity_sweeps.json`. The configured sweep grid
supports inspection of parameter responses, including flat or non-monotone
responses; it does not establish global sensitivity or calibrated uncertainty.
The sweeps are *not* a substitute for a Bayesian
calibration; they are a *contract-stability witness* that says: when
the kernel is asked to change one parameter at a time, the
intermediate states and final outputs respond consistently and within
configured bounds.

This follows the spirit of global sensitivity analysis: the first goal
is not to claim calibrated predictive uncertainty, but to expose which
outputs move under controlled parameter changes and which outputs are
structurally insensitive under the current reduced kernel
[@saltelli2008global].

## Signposting readiness and prioritized gaps

The readiness review writes
`output/reports/project_readiness_review.md` and
`output/reports/project_readiness_review.json`. It currently reports
strict signposting coverage for 72
directories and keeps the next-improvement backlog tied to the
research-suite gaps. The top prioritized improvement is
**BeeBrain calcium acquisition completion (P27)**.

The readiness review is structurally different from the
research-suite report. The research-suite report describes *current
state*; the readiness review describes *recommended next state*.
Keeping the two separated avoids a common failure mode in research
software, where forward-looking optimism leaks into descriptive
artifacts and slowly displaces honest gap reporting.

## Methods panels and manuscript evidence links

The methods-analysis report writes
`output/reports/methods_analysis.md`,
`output/data/methods_analysis.json`,
`output/reports/manuscript_figure_index.md`, and
`output/data/manuscript_figure_index.json`. It reports
5 module methods panels,
3 scenario-sweep panels,
52 linked visualization records, and an
overall methods validation fraction of 0.800.
Its `all_validations_passed` flag is False,
and its highest-priority visible gap is **BeeBrain: template_bank**.

## Registered-check fractions are not biological quality scores

A validation fraction is the share of *registered checks* that
currently pass. It is not a model-quality score, and it is not a
biological-realism score. A fraction of 1.0 means: every check that
the project has decided to run, currently passes. Increasing the
denominator (adding stricter checks) can lower the fraction; that is
a feature, not a bug, because it makes the bar visible.

## Tracing scorecard values to checks and gaps

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

## Responsibilities of integrity, methods, synthesis, and readiness reports

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
