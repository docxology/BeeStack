# Empirical Results

The empirical pipeline is BeeBrain's connection to real *Apis mellifera*
data. It separates anatomy evidence from activity evidence, records
the parseable-source fraction explicitly, and writes one JSON report
per evidence channel so downstream consumers — the manuscript, the
research suite, the methods-analysis pass, and the readiness review —
can audit what was loaded, what was parsed, and what is missing.

## Reports written

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
  anatomy and activity report.

## Anatomy evidence

Anatomy records summarize:

- Honey-Bee Standard Brain atlas assets and ZIP inventories
  [@brandt2005standardbrain];
- VRML/TIFF/HTML metadata derived from the standard-brain ecosystem
  [@rybak2010digital];
- neuropil abbreviations (a vocabulary required to align activity
  panels against atlas regions).

The latest run loads {{ANATOMY_INVENTORY_COUNT}} anatomy inventories.
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

The latest run contains {{EMPIRICAL_PANEL_COUNT}} empirical panels,
{{ANTENNAL_SUMMARY_COUNT}} antennal summaries, and
{{EMPIRICAL_TEMPLATE_COUNT}} integrated templates. The waggle-follower
analysis contributes {{WAGGLE_FOLLOWER_TRACK_COUNT}} tracks with
confidence {{WAGGLE_FOLLOWER_CONFIDENCE}} when the Figshare source is
local and parseable.

## Data completeness

The brain-data completeness panel reports a parseable-source fraction
of {{BRAIN_DATA_PARSEABLE_FRACTION}} and a source-verified fraction of
{{BRAIN_SOURCE_VERIFIED_FRACTION}}. The parseability-readiness flag is
{{BRAIN_PARSEABILITY_TARGET_SATISFIED}} against the recorded 0.800
target, but that flag is not a simple claim that every registered
payload is currently parseable: source-verified gaps can satisfy the
readiness gate only when they carry an explicit blocker, parser status,
and remediation path. Empirically known gaps are catalogued as
`EMPIRICAL_KNOWN_GAP_COUNT = {{EMPIRICAL_KNOWN_GAP_COUNT}}`, and the
dominant current gap is that Paoli MATLAB calcium traces
[@paoli2024dryad] are not yet local or parseable in the current
artifact set. BeeStack records this as a *gap* rather than replacing it
with synthetic data — preserving the distinction between registered
sources, local payloads, parsed summaries, and model inputs.

## Empirical figures

Figures under `output/figures/empirical/` report panel quality, panel
heatmaps, stack alignment, antennal movement, waggle-follower
alignment, waggle-phase coupling, recruitment-decoding inputs, data
completeness, anatomy assets, simplified anatomy projection, neuropil
coverage, and activity summaries. Each figure is registered in the
manuscript figure index with its backend, fidelity tier, and
regeneration command.

![Matplotlib empirical completeness matrix generated from the BeeBrain source registry and parser statuses; sidecar validation checks the raster, and the figure supports availability and blocker claims rather than synthetic completion of absent calcium traces.](../figures/empirical/brain_data_completeness_matrix.png){#fig:brain_data_completeness_matrix}

![Matplotlib empirical multimodal source map generated from BeeBrain anatomy, odor, antennal, and waggle-follower source metadata; sidecar validation checks the raster, and the figure supports source-to-contract traceability rather than completed empirical assimilation.](../figures/empirical/bee_brain_multimodal_source_map.png){#fig:brain_multimodal_source_map}

## Why the gap honesty matters

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
considerations summarized in "Reproducibility" and "Ethics and Data Provenance."
