# Validation and Figure Evidence {#sec:validation}

BeeStack treats visualization as *evidence* only when the backend and
validation status are explicit. A figure without fidelity metadata is not used
as evidence. A figure that declares its provenance, validates its content, and
links back to the script that produced it is reproducible evidence.

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

## Multi-level visual checks

Visual checks operate at several levels:

1. **BeeBody verification** checks non-blank dynamic frames, motion
   pixels per second, locomotion mode (walking vs. flight),
   honeybee MJCF cue presence, silhouette overlap with a reference
   bee shape, and — importantly — *absence* of FlyBody debug aids
   inconsistent with a honeybee render. The latest run reports a
   BeeBody visual score of 0.980 and a silhouette
   score of 1.000.
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

## Textual and structural validation

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
a manuscript figure index with 69 artifact rows.
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

[@fig:beestack_evidence_ladder] ranks evidence tiers against readiness artifacts.

![Matplotlib beestack evidence ladder shows Visual evidence contract separating backend, claim tier, validation status, source data, and unsupported inference for current BeeStack figures. Generated from methods analysis, readiness review, and generated artifact manifests. Sidecar validation checks raster, source routing, and registered claim tier. Does not remove the assimilation, residual, uncertainty, or governance gaps.](../figures/beestack_evidence_ladder.png){#fig:beestack_evidence_ladder}

[@fig:validation_readiness_residuals] lists residual blockers that still prevent digital-twin readiness.

![Matplotlib beestack validation readiness and residual blockers shows Validation-readiness panel separating implemented verification checks from blocked held-out residual, uncertainty, assimilation, and governance evidence. Generated from source refresh ledger, readiness review, generated reports, and figure sidecars. Sidecar validation checks raster, source routing, and registered claim tier. Does not provide held-out residuals, uncertainty quantification, or digital-twin readiness.](../figures/beestack_validation_readiness_residuals.png){#fig:validation_readiness_residuals}

[@fig:manuscript_figure_claim_map] maps registered figures by manuscript section and claim family.

![Matplotlib beestack manuscript figure claim map shows Overview matrix grouping inserted primary figures by manuscript section and registered claim family. Generated from figure registry and manuscript figure index. Sidecar validation checks raster, source routing, and registered claim tier. Does not add empirical evidence beyond the registered figure sidecars.](../figures/manuscript_figure_claim_map.png){#fig:manuscript_figure_claim_map}

[@fig:manuscript_figure_claim_detail] lists the same primary figures with source classes and explicit unsupported-inference boundaries.

![Matplotlib beestack manuscript figure claim detail shows Split companion table listing primary figures, source-data classes, claim tiers, and unsupported-inference boundaries. Generated from figure registry and manuscript figure index. Sidecar validation checks raster, source routing, and registered claim tier. Does not add empirical evidence beyond the registered figure sidecars.](../figures/manuscript_figure_claim_detail.png){#fig:manuscript_figure_claim_detail width=98%}

[@fig:methods_dashboard] summarizes module-level methods panels in one dashboard.

![Matplotlib/pandas/NetworkX beestack methods dashboard shows Methods dashboard summarizing per-module validation, evidence links, visual artifacts, metric counts, and explicit gap counts. Generated from MethodsAnalysisReport module panels and validation panels. Sidecar validation checks raster, source routing, and registered claim tier. Does not support biological predictive validity.](../figures/methods/methods_repo_dashboard.png){#fig:methods_dashboard}

[@fig:methods_dashboard_detail] expands the methods dashboard into a module table with gap and boundary text kept legible at PDF scale.

![Matplotlib/pandas/NetworkX beestack methods dashboard detail shows Split companion table showing module validation fractions, visual artifact counts, evidence-link counts, gap counts, and boundaries. Generated from MethodsAnalysisReport module panels and visual QA report. Sidecar validation checks raster, source routing, and registered claim tier. Does not support biological predictive validity.](../figures/methods/methods_dashboard_detail.png){#fig:methods_dashboard_detail width=98%}

[@fig:methods_evidence_index] links manuscript sections to evidence records and regeneration commands.

![Matplotlib/pandas/NetworkX beestack manuscript evidence index shows Manuscript evidence index comparing evidence-link counts, visual-artifact counts, and validation fractions by BeeStack module. Generated from MethodsAnalysisReport manuscript evidence links. Sidecar validation checks raster, source routing, and registered claim tier. Does not substitute evidence links for absent empirical support.](../figures/methods/methods_manuscript_evidence_index.png){#fig:methods_evidence_index}

## Figure design, accessibility, and claim discipline

The main-manuscript figures follow a reader-facing design contract:
consistent typography and panel structure, restrained non-data ink,
perceptually safer colour choices, contrast checks for text-like marks,
purposeful alt text, position- and length-oriented encodings for the
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

The inserted-figure rule is now stricter than a generic sidecar check:
every raster image promoted into the hydrated manuscript must have a
curated `figure_registry.py` narrative with a manuscript section, Pandoc
label, caption, alt text, claim tier, fidelity tier, source-data field,
regeneration command, and unsupported-inference sentence. Generic
sidecars remain acceptable for supporting diagnostics in the gallery or
generated reports, but not for figures that carry manuscript evidence.
This gives the manuscript figure claim map a complete accounting surface
instead of a partial registry with generic fallbacks.

## Why this matters

The combined effect of these layers is that a reader can audit *any
figure* in this manuscript to determine: which kernel produced it,
what fidelity tier the kernel sits in, whether the figure passed nonblank/quality validation, where its sidecar
metadata lives, and how to regenerate it. That is the operational meaning
of "reproducible research" inside BeeStack: not merely "the code is
public," but "every claim is linkable, every figure is regenerable,
and every fidelity gap is named" [@wilson2017good;
@lamprecht2020fairsoftware].

## Failure modes that visualization catches

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
