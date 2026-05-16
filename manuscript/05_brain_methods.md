# BeeBrain Methods

BeeBrain is a *reduced neural kernel with a real empirical-data surface*.
It implements antennal-lobe encoding, lateral inhibition, sparse Kenyon-cell
coding, central-complex heading integration, optic-flow helpers, Johnston's
organ waggle-event detection, and dance decoding. The default configuration
uses {{GLOMERULI}} glomeruli, {{KC_PER_HEMISPHERE}} Kenyon cells per
hemisphere, {{ACTIVE_KC}} active Kenyon cells at the configured sparsity
bound $\rho = {{KC_SPARSITY}}$, and {{HEADING_BINS}} heading bins.

## Antennal lobe (AL)

The AL channel projects raw olfactory activity through a glomerular
projection layer (one channel per glomerulus, matched to the
Galizia–Sachse [@galizia1999glomerular] canonical odor maps when an
odor template is registered) and a lateral-inhibition operator. The
inhibition kernel is parameterized so it reproduces the contrast
sharpening characteristic of the bee AL [@szyszka2023granger] without
overfitting to a particular preparation. Glomerular activations are
clipped, log-scaled, and bounded so they remain serializable across runs
even when input intensities span orders of magnitude.

## Mushroom body (MB)

The MB layer maps the dense AL representation onto a sparse population
of {{KC_PER_HEMISPHERE}} Kenyon cells per hemisphere. Each Kenyon cell
samples a small fixed fan-in of glomeruli through a seed-fixed sparse
projection, and a $k$-Winner-Take-All rule keeps the
{{ACTIVE_KC}} most-driven cells active across both hemispheres
($\rho = {{KC_SPARSITY}}$ of the whole-brain {{KC_PER_HEMISPHERE}}×2
population). Because the active set is selected by projected drive
rather than from the seed alone, *different odors produce different
sparse codes* — the code is odor-specific and deterministic for a fixed
seed, and changes in odor density do not silently inflate or collapse
the active set. The
class-i Kenyon-cell fraction in the configuration (`kc_class_i_fraction
= 0.90`) tracks the gene-expression bias documented for the honey-bee MB
[@kaneko2016kenyon].

## Central complex (CX)

The CX channel maintains a head-direction estimate on {{HEADING_BINS}}
bins by integrating optic-flow drift and inertial cues, in the spirit of
the anatomically constrained insect path-integration model
[@stone2017central; @honkanen2019sky]. The CX state is part of every
`BrainState` so downstream layers (BeeMind belief updates, BeeSwarm
dance decoding) read a consistent heading.

## Optic flow and visual helpers

A small set of optic-flow helpers downsample the visual observation to a
horizon-aligned signal that the CX can consume. These helpers also feed
the bee-visual signature scorer used by the BeeBody verifier (§4). The
UV–blue–green colour-opponency helper returns three channels that are
constrained to sum to zero, so the opponent code carries two
independent degrees of freedom (the third channel is derived, not an
extra signal).

## Johnston's organ and waggle decoding

The waggle channel transforms antennal-vibration events into candidate
waggle phases, durations, and inferred sun-relative angles. The
configured dance-event rate is 250 Hz; the Johnston's-organ event
detector additionally applies a fixed 200 Hz vibration-frequency floor
(a hard-coded detector primitive, distinct from the configurable event
rate). The dance decoder consumes those candidates plus the CX heading
to produce a recruitment hypothesis in the `BrainState`'s waggle field.
The distance estimate is a reduced-kernel placeholder — a nominal
1 s ↔ 1 km identity, **not** a species-calibrated von Frisch curve.
The Hadjitofi–Webb antennal-position tracks [@hadjitofi2024figshare]
anchor only the follower-orientation diagnostics
(`WaggleFollowerSummary`), not the distance/azimuth decode.

## Empirical registry

The empirical registry anchors the BeeBrain surface to public *Apis
mellifera* sources:

- Paoli antennal-lobe calcium imaging [@paoli2024dryad];
- Galizia–Sachse glomerular odor maps [@galizia1999glomerular];
- Szyszka antennal-lobe Granger-causal dynamics
  [@szyszka2023granger];
- Kaneko Kenyon-cell subtype expression [@kaneko2016kenyon];
- the Virtual Honey-Bee Standard Brain ecosystem
  [@rybak2010digital];
- Carcaud multisite GCaMP workbooks [@carcaud2022dryad];
- Andreu alarm-odorant receptor data [@andreu2025dryad];
- Jernigan antennal active-sensing kinematics
  [@jernigan2026dryad];
- Nouvian biogenic-amine spreadsheets [@nouvian2017dryad];
- Hadjitofi–Webb Figshare waggle-following dataset
  [@hadjitofi2024figshare] (CC BY 4.0).

## Parser layer

The parser layer converts real-format payloads into typed anatomy and
activity records. Atlas ZIP and HTML assets become inventories,
neuropil abbreviation records, and anatomy summaries. Workbook, CSV,
and MAT-style activity payloads become response panels, calcium
summaries when local traces are parseable, antennal-movement summaries,
neuromodulatory summaries, and glomerulus-length templates. Calcium
traces are summarised as *negated* ΔF/F: an excitatory response
(fluorescence increase) yields a negative summary value, so
`excitatory_fraction` counts glomeruli with mean response < 0 and
`inhibitory_fraction` those > 0 — a load-bearing sign convention for
any downstream excitation/inhibition claim. The waggle
parser converts Hadjitofi–Webb follower tracks into
`WaggleFollowerSummary` records that pack follower angle/midpoint
coupling, left/right-antenna synchrony, both-antennae versus
no-antennae decoding error, straightness, and a bounded confidence
score. These templates and diagnostics can be passed directly to
`process_observation`, BeeSwarm recruitment diagnostics, and the
integrated stack run.

## Empirical run integration

The current empirical run integrates {{EMPIRICAL_PANEL_COUNT}}
odor-response panels, {{ANATOMY_INVENTORY_COUNT}} anatomy inventories,
{{ANTENNAL_SUMMARY_COUNT}} antennal-movement summaries, and
{{EMPIRICAL_TEMPLATE_COUNT}} templates. It also records
{{WAGGLE_FOLLOWER_TRACK_COUNT}} waggle-follower tracks when the
Figshare files are local, with follower-decoding confidence
{{WAGGLE_FOLLOWER_CONFIDENCE}} and decoding improvement
{{WAGGLE_DECODING_IMPROVEMENT}}. The brain-data parseable-source
fraction is {{BRAIN_DATA_PARSEABLE_FRACTION}}. The run records
{{CALCIUM_DATASET_COUNT}} local calcium datasets and
{{EMPIRICAL_KNOWN_GAP_COUNT}} empirical known gaps, making *missing
upstream payloads visible* instead of fabricating data.
The source-verified fraction is {{BRAIN_SOURCE_VERIFIED_FRACTION}},
and the 0.800 parseability-readiness target is recorded as
{{BRAIN_PARSEABILITY_TARGET_SATISFIED}} because every remaining
nonparseable source must carry a DOI/source URL, parser status, blocker,
and remediation path.

## Methods-analysis pass

The methods-analysis pass summarizes this evidence as a Brain
completeness panel: enabled dataset count, panel count, template count,
anatomy-inventory count, neuropil count, region-response class count,
odor separability, and calcium-dataset availability. The figure is
written to
`output/figures/methods/beebrain_methods_empirical_completeness.png`,
and the top gap is propagated as {{METHODS_TOP_GAP}}.

![BeeBrain empirical methods completeness](../figures/methods/beebrain_methods_empirical_completeness.png){#fig:brain_methods_completeness}

## Fidelity boundary

BeeBrain is empirically anchored but kinetically reduced. It does not
claim connectome-level dynamics or a heavyweight spiking core. The
contracts that BeeBrain emits (`BrainState`, `WaggleFollowerSummary`,
`AnatomyInventory`) are designed so a spiking simulator can replace the
current AL–MB–CX kernel without breaking BeeMind, BeeSwarm, or the
manuscript-hydration trail.
