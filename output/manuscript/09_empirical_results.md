# Empirical Results {#sec:empirical_results}

The empirical pipeline is BeeBrain's connection to real *Apis mellifera*
data. It separates anatomy evidence from activity evidence, records
the parseable-source fraction explicitly, and writes one JSON report
per evidence channel so downstream consumers — the manuscript, the
research suite, the methods-analysis pass, and the readiness review —
can audit what was loaded, what was parsed, and what is missing.

## Empirical analysis reports

The empirical pipeline writes:

- `output/data/empirical_analysis.json` — workbook, CSV, MAT,
  anatomy, and template-bank summaries plus stack-integration
  diagnostics;
- `output/data/empirical_template_bank.json` — registered odor
  templates with excitation widths, inhibition fractions, and
  glomerulus-length profiles;
- `output/data/waggle_follower_analysis.json` — Hadjitofi–Webb
  waggle-follower antennal-position summaries and BeeBrain/BeeSwarm
  decoding confidence [@hadjitofi2024figshare;
  @hadjitofi2024currentbiology];
- `output/data/brain_data_completeness.json` — curated-source
  downloaded and parseable fractions, plus an explicit module/modality
  matrix;
- `output/data/bee_brain_end_to_end_report.json` — typed BeeBrain
  anatomy and activity report;
- `output/data/bee_brain_connectome.json` — typed structural
  projectome graph (HSB VRML wiring; synaptic tier explicitly unavailable).

## Connectome evidence tiers

BeeStack distinguishes **structural**, **functional**, and **synaptic**
connectome evidence. The generated connectome report tier is
structural_projectome with 95 nodes and
6 structural tract edges; synaptic
edge count is 0. Structural coverage
is 1.000 against the Honeybee Standard
Brain assets on disk [@brandt2005standardbrain]. No public whole-brain
synaptic connectome for *Apis mellifera* is claimed. Szyszka
[@szyszka2023granger] MDPI supplementary Table S1 (Wilcoxon template tests)
is parsed locally; the VAR Granger connectivity matrix remains unavailable
on public deposit (authors provide data on request), so functional Granger
edges are not emitted in `bee_brain_connectome.json`.

## Anatomy evidence

Anatomy records summarize:

- Honey-Bee Standard Brain atlas assets and ZIP inventories
  [@brandt2005standardbrain];
- VRML/TIFF/HTML metadata derived from the standard-brain ecosystem
  [@rybak2010digital];
- neuropil abbreviations (a vocabulary required to align activity
  panels against atlas regions).

The latest run loads 7 anatomy inventories.
These inventories are typed (`AnatomyInventory` dataclasses) and
serialized so that downstream summaries do not have to re-parse the
raw ZIP/HTML payloads at every analysis step.

## Activity evidence

Activity records summarize:

- odor-response panels;
- calcium traces when local payloads are parseable;
- antennal-movement summaries from Jernigan plume-tracking CSVs
  [@jernigan2026dryad];
- waggle-follower antennal-position and dance-vector model-error
  summaries from Hadjitofi–Webb [@hadjitofi2024figshare;
  @hadjitofi2024currentbiology];
- neuromodulatory spreadsheets from Nouvian biogenic-amine assays
  [@nouvian2017dryad];
- template-bank integration (Galizia–Sachse glomerular maps
  [@galizia1999glomerular] combined with Szyszka transient
  dynamics [@szyszka2023granger]).

The latest run contains 48 empirical panels,
1 antennal summaries, and
24 integrated templates. The waggle-follower
analysis contributes 59 tracks with
confidence 0.289 when the Figshare source is
local and parseable.

## Data completeness

The brain-data completeness panel reports a parseable-source fraction
of 0.800 and a source-verified fraction of
1.000. The parseability-readiness flag is
True against the recorded 0.800
target. That flag reflects the parseable-source fraction only; source-verified
records with explicit blockers are tracked separately and do not substitute for
missing parseable payloads. In the current generated evidence snapshot,
10 curated BeeBrain sources are registered,
8 have local payloads,
8 are parseable, and
2 source-verified records remain
blocked with explicit remediation notes. Empirically known gaps are catalogued as
`EMPIRICAL_KNOWN_GAP_COUNT = 0`. The Paoli
MATLAB calcium archive [@paoli2024dryad] is now downloaded and parsed
into empirical response summaries, where it serves as a citation anchor;
it is not yet wired as a model input or held-out validation target, so
its contribution remains evidentiary rather than integrative. BeeStack
preserves this distinction between registered sources, local payloads,
parsed summaries, and model inputs rather than fabricating synthetic
traces to claim integration it has not yet performed.

## Empirical figures

Figures under `output/figures/empirical/` report panel quality, panel
heatmaps, stack alignment, antennal movement, waggle-follower
alignment, waggle-phase coupling, recruitment-decoding inputs, data
completeness, anatomy assets, simplified anatomy projection, neuropil
coverage, and activity summaries. Each figure is registered in the
manuscript figure index with its backend, fidelity tier, and
regeneration command.

[@fig:connectome_structural_graph] shows the structural-projectome graph as an
availability witness, not a synaptic-connectome claim.

![Matplotlib beebrain structural projectome graph shows Network layout of Honeybee Standard Brain neuropils, named neuron/tract nodes, and documented structural tract edges. Generated from output/data/bee_brain_connectome.json. Sidecar validation checks raster, source routing, and registered claim tier. Does not claim synaptic adjacency or functional Granger completeness.](../figures/empirical/connectome_structural_graph.png){#fig:connectome_structural_graph}

[@fig:connectome_completeness_tiers] separates structural, functional, and
synaptic tiers so unavailable evidence stays visible.

![Matplotlib connectome evidence tiers shows Coverage bars for structural, functional, and synaptic connectome tiers with synaptic tier explicitly unavailable. Generated from output/data/brain_data_completeness.json. Sidecar validation checks raster, source routing, and registered claim tier. Does not upgrade unavailable tiers into supported claims.](../figures/empirical/connectome_completeness_tiers.png){#fig:connectome_completeness_tiers}

[@fig:empirical_panel_heatmap] gives the reader the panel-level empirical
response surface used by the reduced BeeBrain summaries.

![Matplotlib empirical odor-response panel heatmap shows Heatmap of the first registered empirical odor-response panel showing channel responses across stimuli. Generated from output/data/empirical_analysis.json. Sidecar validation checks raster, source routing, and registered claim tier. Does not support connectome-scale or calcium-validated dynamics.](../figures/empirical/empirical_panel_heatmap.png){#fig:empirical_panel_heatmap}

[@fig:empirical_stack_alignment] reports alignment between available empirical
templates and the reduced module contracts without claiming biological
ground-truth calibration.

![Matplotlib beebrain empirical stack alignment shows Alignment scores between empirical templates and reduced BeeBrain module contracts. Generated from output/data/empirical_analysis.json. Sidecar validation checks raster, source routing, and registered claim tier. Does not calibrate reduced kernels to biological ground truth.](../figures/empirical/empirical_stack_alignment.png){#fig:empirical_stack_alignment}

[@fig:empirical_anatomy_projection] projects Honeybee Standard Brain geometry
into a manuscript-visible atlas witness.

![Matplotlib honeybee standard brain vrml projection shows VRML geometry centroids with structural tract overlays when the connectome report is available. Generated from output/data/bee_brain_connectome.json. Sidecar validation checks raster, source routing, and registered claim tier. Does not infer functional or synaptic connectivity.](../figures/empirical/empirical_anatomy_projection.png){#fig:empirical_anatomy_projection}

[@fig:empirical_activity_summary] condenses the current activity evidence while
preserving the calcium-availability boundary.

![Matplotlib beebrain empirical activity summary shows Reduced activity summary combining odor separability, calcium fractions, aftersmell response, and antennal drive. Generated from output/data/empirical_analysis.json. Sidecar validation checks raster, source routing, and registered claim tier. Does not support calcium-validated dynamics; parsed calcium traces are a citation anchor, not a model input.](../figures/empirical/empirical_activity_summary.png){#fig:empirical_activity_summary}

[@fig:waggle_follower_alignment] maps local Hadjitofi-Webb follower summaries
to BeeStack decoding confidence without validating colony-scale recruitment.

![Matplotlib waggle follower empirical alignment shows Hadjitofi–Webb follower antennal alignment metrics mapped to BeeStack decoding confidence. Generated from output/data/waggle_follower_analysis.json. Sidecar validation checks raster, source routing, and registered claim tier. Does not validate colony-scale recruitment.](../figures/empirical/waggle_follower_alignment.png){#fig:waggle_follower_alignment}

[@fig:brain_data_completeness_matrix] summarizes parseable empirical panels and known gaps.

![Matplotlib brain data completeness matrix shows Empirical completeness matrix showing which BeeBrain source rows are registered, locally available, parseable, and source-verified. Generated from output/data/brain_data_completeness.json. Sidecar validation checks raster, source routing, and registered claim tier. Does not replace absent calcium payloads with synthetic traces.](../figures/empirical/brain_data_completeness_matrix.png){#fig:brain_data_completeness_matrix}

[@fig:brain_multimodal_source_map] maps multimodal BeeBrain sources to assimilation status.

![Matplotlib beebrain multimodal source map shows Multimodal source map organizing anatomy, odor-response, antennal, and waggle-follower records by integration target and local availability. Generated from output/data/brain_data_completeness.json and empirical analysis report. Sidecar validation checks raster, source routing, and registered claim tier. Does not support a complete multimodal empirical assimilation pipeline.](../figures/empirical/bee_brain_multimodal_source_map.png){#fig:brain_multimodal_source_map}

## Why the gap honesty matters

A reduced BeeBrain that substitutes synthetic values for missing calcium
traces would still produce a complete-looking manuscript. The gap-explicit
design here deliberately makes incompleteness visible in the hydrated
manuscript: `BRAIN_DATA_PARSEABLE_FRACTION =
0.800` and `EMPIRICAL_KNOWN_GAP_COUNT =
0` are not editorial choices; they are
the same values the readiness review and research-suite scorecards
read. A reviewer can read the manuscript, the JSON reports, and the
readiness review without having to cross-check that they tell the
same story — because all three are hydrated from the same
machine-readable artifacts.

## Provenance trail

Raw empirical downloads live in `output/data/empirical_sources/` and
are documented by `catalog.json`, `archives.json`, and
`anatomy_downloads.json` so that every dataset, its DOI, its
publication, its CC license, and the date of download are recorded.
This trail is essential for the data-provenance and ethics
considerations summarized in [@sec:reproducibility] and [@sec:ethics].
