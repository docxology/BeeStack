# Validation and Figure Evidence

BeeStack treats visualization as *evidence* only when the backend and
validation status are explicit. A figure without fidelity metadata is not used
as evidence. A figure that declares its provenance, validates its content, and
links back to the script that produced it is reproducible evidence.

## Animation manifest

The animation manifest currently contains {{ANIMATION_COUNT}}
animations: {{REAL_FLYBODY_ANIMATION_COUNT}} FlyBody/MuJoCo
outputs and {{REDUCED_ANIMATION_COUNT}} reduced schematic outputs. The
real group contains BeeBody walking, BeeBody flight, the
BeeSwarm ten-bee collision scene, the BeeSwarm configured waggle dance,
and the long multi-BeeBody waggle-dance scenario. Reduced schematic
outputs are retained for module-level Brain, Mind, recruitment-field
Swarm, and Niche summaries — they are *explanatory*, not biomechanical.

## Multi-level visual checks

Visual checks operate at several levels:

1. **BeeBody verification** checks non-blank dynamic frames, motion
   pixels per second, locomotion mode (walking vs. flight),
   honeybee MJCF cue presence, silhouette overlap with a reference
   bee shape, and — importantly — *absence* of FlyBody debug aids
   inconsistent with a honeybee render. The latest run reports a
   BeeBody visual score of {{BEE_VISUAL_SCORE}} and a silhouette
   score of {{BEE_SILHOUETTE_SCORE}}.
2. **BeeSwarm verification** requires MuJoCo contact reports for
   strict scenes. A strict scene with zero unique contact pairs is
   rejected as evidence; the methods-analysis pass currently records
   {{METHODS_SWARM_CONTACT_PAIR_COUNT}} unique bee-contact pairs and
   {{STRICT_SWARM_SCENE_COUNT}} strict scenes, including a long
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
  {{SIGNPOSTED_DIRECTORY_COUNT}} signposted directories and
  prioritizes the next-improvement backlog from the research gaps —
  the current top priority is {{READINESS_TOP_PRIORITY}}.

## Methods-analysis figures

The methods-analysis pass adds {{METHODS_FIGURE_COUNT}} static methods
figures, JSON sidecar metadata for generated methods and research figures,
{{METHODS_EVIDENCE_LINK_COUNT}} manuscript evidence links, and a source-claim
crosswalk that carries module, method, configuration tokens, artifact path,
citation keys, source DOIs, claim tier, and availability status. It also writes
a manuscript figure index with {{MANUSCRIPT_FIGURE_INDEX_COUNT}} artifact rows.
The index maps every cited figure or visual artifact to
its backend (e.g. FlyBody, MuJoCo, Matplotlib), fidelity level (real
3D, reduced kernel, schematic), validation status (passed/passed with
caveats/known gap), and the regeneration command needed to reproduce
it. The evidence ladder in
`output/figures/beestack_evidence_ladder.png` is the reader-facing version of
that contract: it separates strict rendered physics, empirical availability,
reduced kernels, compatibility summaries, and the still-blocked digital-twin
claim.

![Matplotlib BeeStack evidence ladder generated from methods analysis, readiness review, and artifact manifests; sidecar validation checks the raster, and the figure states which visual tiers support current claims rather than digital-twin readiness.](../figures/beestack_evidence_ladder.png){#fig:beestack_evidence_ladder}

![Matplotlib validation-readiness panel generated from source-refresh records, readiness review, generated reports, and figure sidecars; sidecar validation checks the raster, and the figure shows implemented checks and blocked residual, uncertainty, assimilation, and governance evidence rather than drawing invented residual bars.](../figures/beestack_validation_readiness_residuals.png){#fig:validation_readiness_residuals}

![Matplotlib manuscript figure claim map generated from the figure registry and manuscript figure index; sidecar validation checks the raster, and the figure supports figure-provenance review rather than adding empirical evidence.](../figures/manuscript_figure_claim_map.png){#fig:manuscript_figure_claim_map}

![Matplotlib/pandas BeeStack methods dashboard generated from MethodsAnalysisReport; sidecar validation checks the raster, and the figure supports provenance and validation coverage claims rather than biological predictive validity.](../figures/methods/methods_repo_dashboard.png){#fig:methods_dashboard}

![Matplotlib/pandas manuscript evidence index generated from MethodsAnalysisReport evidence links; sidecar validation checks the raster, and the figure supports manuscript provenance coverage rather than absent empirical support.](../figures/methods/methods_manuscript_evidence_index.png){#fig:methods_evidence_index}

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
