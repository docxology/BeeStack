# Empirical Results and Current Data Availability {#sec:empirical_results}

The aggregate empirical pipeline connects BeeBrain to local *Apis mellifera*
data only after at least one parseable odor-response panel is present. A
successful aggregate separates anatomy from activity evidence and writes
channel-specific reports. With no odor panel, the aggregate remains unavailable:
standalone parsers may still read other local modalities, but retained reports
are not automatically promoted to current observations.

Current odor-response analysis availability: `{{EMPIRICAL_AVAILABILITY}}`.
When payloads are absent, N/A denotes unavailable current measurements.
Retained empirical reports and figures are historical snapshots, explicitly
marked in their sidecars/index; they do not establish current data availability.

## Odor-panel-gated aggregate reports

When that prerequisite is met, the empirical pipeline writes:

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
- `output/data/bee_brain_connectome.json` — a schematic pathway graph when
  supporting assets are absent, with separately identified structural links
  only where local HSB VRML files support them; synaptic evidence remains unavailable.

## Schematic, structural, functional, and synaptic evidence tiers

BeeStack distinguishes **structural**, **functional**, and **synaptic**
connectome evidence. The generated connectome report tier is
{{CONNECTOME_TIER}} with {{CONNECTOME_NODE_COUNT}} nodes and
{{CONNECTOME_STRUCTURAL_EDGE_COUNT}} structural tract edges; synaptic
edge count is {{CONNECTOME_SYNAPTIC_EDGE_COUNT}}. Structural coverage
is {{CONNECTOME_STRUCTURAL_COVERAGE}} against the Honeybee Standard
Brain assets on disk [@brandt2005standardbrain]. No public whole-brain
synaptic connectome for *Apis mellifera* is claimed. A standalone parser can
read the Szyszka [@szyszka2023granger] supplementary Table S1 Wilcoxon tests
when that supplement is local. Those tests are not a VAR Granger matrix;
functional Granger edges are not emitted merely from parsing the table.

## Anatomy evidence

Anatomy records summarize:

- Honey-Bee Standard Brain atlas assets and ZIP inventories
  [@brandt2005standardbrain];
- VRML/TIFF/HTML metadata derived from the standard-brain ecosystem
  [@rybak2010digital];
- neuropil abbreviations (a vocabulary required to align activity
  panels against atlas regions).

The current aggregate contains {{ANATOMY_INVENTORY_COUNT}} anatomy inventories
when available. `AtlasInventory` records serialize ZIP/VRML summaries;
an absent aggregate does not certify that every standalone anatomy input is absent.

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
- template-bank integration from compatible observed odor panels or recordings;
  the Galizia–Sachse source [@galizia1999glomerular] remains a citation anchor
  until its matrix is registered, and Szyszka Table S1 [@szyszka2023granger]
  statistics are not transient recordings or a connectivity matrix.

When a current aggregate is available, it contains {{EMPIRICAL_PANEL_COUNT}}
empirical panels, {{ANTENNAL_SUMMARY_COUNT}} antennal summaries, and
{{EMPIRICAL_TEMPLATE_COUNT}} integrated templates. Standalone waggle-follower
analysis may report {{WAGGLE_FOLLOWER_TRACK_COUNT}} tracks and confidence
{{WAGGLE_FOLLOWER_CONFIDENCE}} when its Figshare inputs are local and parseable;
this does not establish availability of the odor-conditioned aggregate.

## Parseability, source verification, and missing payloads

The brain-data completeness panel reports a parseable-source fraction
of {{BRAIN_DATA_PARSEABLE_FRACTION}} and a source-verified fraction of
{{BRAIN_SOURCE_VERIFIED_FRACTION}}. The parseability-readiness flag is
{{BRAIN_PARSEABILITY_TARGET_SATISFIED}} against the recorded {{BRAIN_PARSEABILITY_TARGET}}
target. That flag reflects the parseable-source fraction only; source-verified
records with explicit blockers are tracked separately and do not substitute for
missing parseable payloads. In the current generated evidence snapshot,
{{BRAIN_SOURCE_DATASET_COUNT}} curated BeeBrain sources are registered,
{{BRAIN_DOWNLOADED_DATASET_COUNT}} have local payloads,
{{BRAIN_PARSEABLE_DATASET_COUNT}} are parseable, and
{{BRAIN_SOURCE_VERIFIED_BLOCKED_COUNT}} source-verified records remain
blocked with explicit remediation notes. Empirically known gaps are catalogued as
`EMPIRICAL_KNOWN_GAP_COUNT = {{EMPIRICAL_KNOWN_GAP_COUNT}}`. The current
run records {{CALCIUM_DATASET_COUNT}} parsed calcium datasets. The Paoli
archive [@paoli2024dryad] remains acquisition-gated when the manifest records
an authorization failure or absent payload; a registered source or downloaded
README is not a parsed calcium recording. When compatible recordings are
present, the pipeline can derive response templates for the integrated bank.
Neither parsing nor template alignment establishes held-out predictive or
biological validation. No synthetic traces replace missing empirical data.

## Historical figures versus current empirical evidence

Historical empirical images remain under `output/figures/empirical/` for
inspection and custody. They are not embedded here as current results while
their generating inputs cannot be re-established. The
[figure index](../../output/reports/manuscript_figure_index.md) records each
artifact's availability, backend, claim tier and regeneration command.

Panel heatmaps and alignment plots require current odor-response inputs.
Anatomy projections require actual geometry; documented schematic pathways do
not acquire measured coordinates. Waggle plots require the corresponding
follower records, and calcium summaries require compatible recordings. A
retained PNG, successful parse or readable sidecar does not satisfy those
scientific prerequisites. Newly generated synthetic/model figures elsewhere
in this manuscript remain explicitly separate from biological observations.

## Missing measurements remain unavailable

A reduced BeeBrain that substitutes synthetic values for missing calcium
traces would still produce a complete-looking manuscript. The gap-explicit
design here deliberately makes incompleteness visible in the hydrated
manuscript: `BRAIN_DATA_PARSEABLE_FRACTION =
{{BRAIN_DATA_PARSEABLE_FRACTION}}` and `EMPIRICAL_KNOWN_GAP_COUNT =
{{EMPIRICAL_KNOWN_GAP_COUNT}}` are not editorial choices; they are
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
