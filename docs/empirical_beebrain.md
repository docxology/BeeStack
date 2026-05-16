# Empirical BeeBrain Data

BeeBrain is a reduced neural kernel with a real empirical-data surface. The
registry, download planner, parsers, validation records, figures, and reports
make the fidelity boundary explicit.

## Registered Anatomy Sources

- `virtual-honeybee-standard-brain`: FU Berlin Honeybee Standard Brain
  gray-value TIFF/JPG images, label-field TIFFs, VRML atlas/neuron/tract ZIP
  files, and neuropil abbreviation metadata.
- DOI: `10.1002/cne.20644`
- Source: [Virtual Honeybee Standard Brain](https://www.bcp.fu-berlin.de/en/biologie/arbeitsgruppen/neurobiologie/ag_menzel/beebrain/index.html)

Anatomy parsing produces `AtlasDownloadRecord`, `AtlasInventory`,
`NeuropilAbbreviation`, and `BeeBrainAnatomySummary` records. These records
support atlas asset tables, neuropil-label coverage, and simplified projection
figures. They do not claim full atlas registration.

## Registered Activity Sources

- `dryad-paoli-2024-al-calcium`: Dryad calcium-imaging matrices for honeybee
  antennal-lobe odor responses, including glomerulus-by-odorant-by-trial-by-time
  arrays.
- `galizia-1999-glomerular-code`: conserved glomerular odor maps for the
  honeybee antennal lobe.
- `szyszka-2023-granger-al-network`: 100 Hz antennal-lobe calcium dynamics and
  functional-connectivity analysis.
- `kaneko-2016-kenyon-subtypes`: honeybee Kenyon-cell subtype evidence for
  mushroom-body constraints.
- `dryad-carcaud-2022-multisite-gcamp`: Dryad workbook data from pan-neuronal
  GCaMP6f multisite honeybee brain imaging across antennal lobe, lateral horn,
  and mushroom-body calyces.
- `dryad-andreu-2025-alarm-odorant-receptors`: Dryad supplementary workbook for
  honeybee alarm-pheromone odorant receptors AmOR136 and AmOR11.
- `dryad-jernigan-2026-antennal-movement`: Dryad frame-level antennal active
  sensing CSV for plume-structure experiments.
- `dryad-nouvian-2017-biogenic-amines`: Dryad brain biogenic-amine and
  cooperative-defence spreadsheets.
- `figshare-hadjitofi-2024-waggle-following`: CC BY 4.0 Hadjitofi-Webb
  Figshare CSV files with follower positions, antenna angles, binned features,
  orientation straightness, and model vector-error outputs for waggle decoding.

## Implemented Calibration Surface

- `negative_delta_f_over_f()`
- `summarize_calcium_trials()`
- `empirical_odor_response_templates()`
- `empirical_alignment_score()`
- `process_observation()`
- `parse_paoli_matlab_payload()`
- `parse_tabular_odor_response_rows()`
- `summarize_antennal_movement_rows()`
- `summarize_waggle_follower_rows()`
- `antennal_vibration_from_movement()`
- `waggle_vibration_from_followers()`
- `bee_brain_data_completeness_panel()`
- `atlas_inventory_from_zip()`
- `neuropil_abbreviations_from_html()`
- `activity_summary_from_components()`

The `beestack.empirical` config section controls enabled dataset IDs, calcium
acquisition rate, baseline/stimulus windows, trial and bee counts, tracked
glomeruli, atlas range, odor-template names, and template
excitation/inhibition widths.

## Fetching Source Files

```bash
uv run python scripts/fetch_empirical_bee_data.py
uv run python scripts/fetch_empirical_bee_data.py --metadata-only
uv run python scripts/analyze_empirical_bee_data.py
```

The fetcher writes:

- `output/data/empirical_sources/catalog.json`
- `output/data/empirical_sources/archives.json`
- `output/data/empirical_sources/anatomy_downloads.json`

The analyzer writes:

- `output/data/empirical_analysis.json`
- `output/data/empirical_template_bank.json`
- `output/data/bee_brain_end_to_end_report.json`
- `output/data/waggle_follower_analysis.json`
- `output/data/brain_data_completeness.json`
- `output/reports/empirical_analysis.md`
- `output/reports/waggle_follower_analysis.md`
- `output/figures/empirical/empirical_panel_heatmap.png`
- `output/figures/empirical/empirical_panel_quality.png`
- `output/figures/empirical/empirical_stack_alignment.png`
- `output/figures/empirical/empirical_antennal_movement.png`
- `output/figures/empirical/empirical_anatomy_assets.png`
- `output/figures/empirical/empirical_anatomy_projection.png`
- `output/figures/empirical/empirical_neuropil_coverage.png`
- `output/figures/empirical/empirical_activity_summary.png`
- `output/figures/empirical/waggle_follower_alignment.png`
- `output/figures/empirical/waggle_phase_coupling.png`
- `output/figures/empirical/beeswarm_waggle_recruitment_diagnostics.png`
- `output/figures/empirical/brain_data_completeness_matrix.png`
- `output/figures/empirical/bee_brain_multimodal_source_map.png`

## Activity Metrics

`BeeBrainActivitySummary` reports calcium latency, inhibitory/excitatory
fractions, empirical odor separability, aftersmell/post-odor response,
AL/LH/MB/receptor/neuromodulatory response summaries, Jernigan antennal
active-sensing drive, Hadjitofi-Webb waggle follower decoding confidence, and
Nouvian neuromodulatory defence summaries when parseable.

## Current Fidelity

The code validates and integrates real downloaded workbook/CSV/MAT/anatomy
payloads when they are present. The default neural dynamics remain deterministic
and reduced: AL templates, Kenyon sparse coding, a heading ring, waggle decoding,
active-sensing drive, and empirical-alignment diagnostics. BeeStack does not yet
claim full spiking dynamics, full connectome simulation, or full standard-brain
registration.
