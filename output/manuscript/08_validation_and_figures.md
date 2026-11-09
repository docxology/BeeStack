# Verification Gates, Evidence Tiers, and Figure Provenance {#sec:validation}

Visualization is eligible for evidence only with explicit backend, source,
availability, fidelity tier, and regeneration provenance. Image-integrity and
metadata checks do not validate scientific interpretation: each claim still
requires appropriate computation, observations, and validation. A provenance
declaration alone is not proof of reproducibility or biological agreement.

## Animation manifest

The animation manifest currently contains 9
animations: 5 FlyBody/MuJoCo
outputs and 4 reduced schematic outputs. The
real group contains BeeBody walking, BeeBody flight, the
BeeSwarm ten-bee collision scene, the BeeSwarm configured waggle dance,
and the long multi-BeeBody waggle-dance scenario. Reduced schematic
outputs are retained for module-level Brain, Mind, recruitment-field
Swarm, and Niche summaries — they are *explanatory*, not biomechanical.

The strict FlyBody/MuJoCo contact sheets in
[@sec:methods_body_swarm] — [@fig:beebody_flybody_morphology],
[@fig:beebody_flybody_flight], [@fig:beeswarm_10_beebody_collision],
[@fig:beeswarm_waggle_dance_configured], and
[@fig:beeswarm_waggle_dance_long] — are the print-facing witnesses for
those five real animations. Each sheet samples eight frames from the
registered GIF; verification scores and contact reports in
`output/reports/bee_visual_verification.md` and
`output/reports/flybody_contact_physics.md` bind the pixels to claim tier.

## Frame, morphology, contact, and accessibility checks

Visual checks operate at several levels:

1. **BeeBody verification** checks non-blank dynamic frames, changed RGB
   channel values across frames, honeybee MJCF cue names, rendered color
   statistics, and absence of cyan debug aids. Walking/flight are requested
   render-mode labels, not inferred gait classifications. The field named
   silhouette score is a cue heuristic, not overlap with a reference image.
   The latest run reports visual score 0.991 and
   MJCF/color cue score 1.000.
2. **BeeSwarm verification** requires MuJoCo contact reports for
   strict scenes. A strict scene with zero unique contact pairs is
   rejected as evidence; the methods-analysis pass currently records
   15.000 unique bee-contact pairs and
   3 strict scenes, including a long
   BeeBody-backed waggle rollout with its own scene XML and contact
   report.
3. **Research figures** are checked for non-blank static image
   content (rejected if the histogram has fewer than a configured
   number of distinct intensities, since a stalled renderer
   typically writes a uniform frame).
4. **Accessibility captions and alt text** are stored in the
   animation manifest so downstream PDFs and web renders can produce
   accessible output without the human author having to retype them.

## Integrity, documentation, and readiness audits

Validation is also textual and structural.

- The **integrity review**
  (`output/reports/beestack_integrity_review.md`) records public APIs,
  contracts, configuration knobs, diagnostics, empirical evidence,
  fidelity labels, and known gaps for every module. It is generated
  from the same source code that the rest of the pipeline imports, so
  it cannot drift from the implementation.
- The **documentation audit**
  (`output/reports/documentation_audit.md`) checks
  generated-output references, manuscript hydration, fidelity
  language, signposting coverage, Pandoc citation keys, required
  BibTeX DOI/URL metadata, registry DOI coverage, and conservative
  digital-twin wording.
- The **readiness review**
  (`output/reports/project_readiness_review.md`) records
  72 signposted directories and
  prioritizes the next-improvement backlog from the research gaps —
  the current top priority is BeeBrain calcium acquisition completion (P27).

## Methods-analysis figures

The methods-analysis pass adds 8 static methods
figures, JSON sidecar metadata for generated methods and research figures,
6 manuscript evidence links, and a source-claim
crosswalk that carries module, method, configuration tokens, artifact path,
citation keys, source DOIs, claim tier, and availability status. It also writes
a manuscript figure index with 75 artifact rows.
The index maps every cited figure or visual artifact to
its backend (e.g. FlyBody, MuJoCo, Matplotlib), fidelity level (real
3D, reduced kernel, schematic), validation status (passed/passed with
caveats/known gap), and the regeneration command needed to reproduce
it. The evidence ladder in
`output/figures/beestack_evidence_ladder.png` is the reader-facing version of
that contract: it separates strict rendered physics, empirical availability,
reduced kernels, compatibility summaries, and the still-blocked digital-twin
claim.

## Security posture validation

Alongside figure, source, and documentation audits, BeeStack runs a static
security posture gate (`output/reports/security_posture_audit.json`) that
verifies curated download host allowlisting, zip-member safety checks, absence
of forbidden orchestration patterns, and presence of the repository threat
model (`BeeStack-threat-model.md`). This gate does not replace penetration
testing or infrastructure hardening; it makes the **implemented** software
controls auditable alongside the evidence ladder. Operational detail lives in
[@sec:ethics] and `docs/security_posture.md`.

The validation figures below separate overview and detail surfaces: evidence
tiers, residual readiness blockers, manuscript claim routing, module-level
methods state, and manuscript evidence links. Each insert states its backend,
source report, sidecar validation, and blocked inference in the caption text.

[@fig:beestack_evidence_ladder] separates conceptual evidence classes and claim ceilings; it does not rank current validation.

![Conceptual guide to evidence classes, potential evidence surfaces, and unsupported inferences; it is not a current availability or validation report. Generated from conceptual evidence-class and claim-ceiling contract using Matplotlib. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not remove the assimilation, residual, uncertainty, or governance gaps.](../figures/beestack_evidence_ladder.png){#fig:beestack_evidence_ladder}

[@fig:validation_readiness_residuals] lists residual blockers that still prevent digital-twin readiness.

![Conceptual checklist separating local verification contracts from absent held-out residual, uncertainty, assimilation, and governance evidence. It is not a receipt that local checks passed. Generated from declared verification, validation, and digital-twin requirements using Matplotlib. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not provide held-out residuals, uncertainty quantification, or digital-twin readiness.](../figures/beestack_validation_readiness_residuals.png){#fig:validation_readiness_residuals}

[@fig:manuscript_figure_claim_map] maps registered figures by manuscript section and claim family.

![Registry-derived counts of primary figures by canonical manuscript section and declared claim family; registration is not evidence strength or insertion status. Generated from figure registry and manuscript figure index using Matplotlib. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not add empirical evidence beyond the registered figure sidecars.](../figures/manuscript_figure_claim_map.png){#fig:manuscript_figure_claim_map}

[@fig:manuscript_figure_claim_detail] groups registered primary sources and claim ceilings; full per-artifact routes remain in the raw inventory and registry.

![Grouped source classes with registered artifact counts, declared claim-family counts, and conservative claim ceilings. Full per-artifact routes and unsupported inferences remain in the registry and raw inventory. Generated from figure registry and manuscript figure index using Matplotlib. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not add empirical evidence beyond the registered figure sidecars.](../figures/manuscript_figure_claim_detail.png){#fig:manuscript_figure_claim_detail width=98%}

[@fig:methods_dashboard] tabulates configured self-test fractions and native module-inventory counts.

![Per-module configured self-test fractions and separate metric, artifact, evidence-link, and known-gap counts without normalization or a composite score. Generated from MethodsAnalysisReport module panels and validation panels using Matplotlib/pandas. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not support biological predictive validity.](../figures/methods/methods_repo_dashboard.png){#fig:methods_dashboard}

[@fig:methods_dashboard_detail] expands the methods dashboard into a module table with gap and boundary text kept legible at PDF scale.

![Module configured self-test fractions, visual-artifact counts, evidence-link counts, known-gap counts, and full report interpretations. Generated from MethodsAnalysisReport module panels and visual QA report using Matplotlib/pandas. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not support biological predictive validity.](../figures/methods/methods_dashboard_detail.png){#fig:methods_dashboard_detail width=98%}

[@fig:methods_evidence_index] separates evidence-link/artifact counts from configured self-test fractions on independent axes.

![Evidence-link and artifact counts in one panel, with configured self-test fractions on a separate axis in the companion panel. Generated from MethodsAnalysisReport manuscript evidence links using Matplotlib/pandas. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not substitute evidence links for absent empirical support.](../figures/methods/methods_manuscript_evidence_index.png){#fig:methods_evidence_index}

## Figure design, accessibility, and claim discipline

The main-manuscript figures follow a reader-facing design contract:
consistent typography and panel structure, restrained non-data ink,
perceptually safer colour choices, configured foreground/background contrast
diagnostics, purposeful alt text, position- and length-oriented encodings for the
main evidence maps, and captions that name the backend, source data,
validation status, and unsupported inference. The design rules are
grounded in practical figure guidance, graphical-perception evidence,
colour-map misuse literature, WCAG contrast/accessibility standards,
FAIR provenance principles, and visual-analytics provenance frameworks
[@rougier2014figures; @cleveland1984graphical; @crameri2020colour;
@w3c2023wcag21; @wilkinson2016fair; @heer2012interactive;
@ragan2016provenance]. The implementation is deliberately mechanical:
sidecars record accessibility checks, design citations, source-data
classes, and claim-tier boundaries, and the figure audit fails if a
primary manuscript caption omits the
backend/source/validation/conservative-interpretation pattern.

Automatic contrast metadata evaluates the supplied foreground/background pair,
using the default text pair when no artifact-specific pair is supplied. It does
not inspect all rendered colors, overlap, PDF-scale legibility, keyboard access,
or screen-reader behavior and is not an artifact-wide WCAG certification.
Rendered PDF and browser inspection remain separate required evidence.

The inserted-figure rule is now stricter than a generic sidecar check:
every raster image promoted into the hydrated manuscript must have a
curated `figure_registry.py` narrative with a manuscript section, Pandoc
label, caption, alt text, claim tier, fidelity tier, source-data field,
regeneration command, and unsupported-inference sentence. Generic
sidecars remain acceptable for supporting diagnostics in the gallery or
generated reports, but not for figures that carry manuscript evidence.
This gives the manuscript figure claim map a complete accounting surface
instead of a partial registry with generic fallbacks.
Raw plot-data payloads preserve unavailable observations as null and retain each
quantity's native units. Sweep outputs use independent native-unit axes; mixed
counts, fractions, and unlike-unit metrics belong in labeled tables or separate
panels. Empirical correlations remain signed correlations and angles retain their
angular units. Layout, sidecar, and nonblank checks are engineering checks, not
new biological observations or held-out validation.

## Figure-level backend and provenance traceability

The combined effect of these layers is that a reader can audit *any
figure* in this manuscript to determine: which kernel produced it,
what fidelity tier the kernel sits in, whether the figure passed nonblank/quality validation, where its sidecar
metadata lives, and how to regenerate it. That is the operational meaning
of "reproducible research" inside BeeStack: not merely "the code is
public," but "every claim is linkable, every figure is regenerable,
and every fidelity gap is named" [@wilson2017good;
@lamprecht2020fairsoftware].

## Renderer, body-plan, and contact failure checks

Empirically, the visual-validation layer catches three recurring
failure modes that pure-numerical validation does not:

1. **Renderer stalls** — a frame loop that emits identical frames is
   detected by the non-blank/motion-pixel checks even when JSON
   diagnostics look healthy.
2. **Body-plan regressions** — a wing or antenna disappearing from
   the MJCF is detected by the MJCF-cue and silhouette checks
   before it propagates to the animation manifest.
3. **Contact-physics gaps** — a multi-bee scene that does not
   produce any unique contact pairs (a configuration error in the
   contact-proxy geoms) is rejected as evidence before it reaches the
   methods-analysis Swarm panel.

Each failure mode is represented by a generated diagnostic or
regression-style test in `tests/`, so the manuscript claim stays at the
level of what the validators check rather than undocumented debugging
history.
