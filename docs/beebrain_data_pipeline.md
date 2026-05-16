# BeeBrain Data Pipeline

BeeBrain has an end-to-end empirical pipeline for curated honeybee anatomy and
activity sources. The pipeline downloads public payloads, records provenance,
parses local archives, validates typed records, analyzes activity/anatomy
summaries, generates figures, and writes JSON/Markdown reports.

## Commands

```bash
uv run python scripts/fetch_empirical_bee_data.py
uv run python scripts/analyze_empirical_bee_data.py
uv run python scripts/analysis_pipeline.py
uv run python scripts/audit_documentation.py
```

`fetch_empirical_bee_data.py` performs full curated downloads by default. It
skips files that already exist and are non-empty. `--metadata-only` writes
catalog manifests without downloading missing payloads. `--force` re-downloads
local files.

## Anatomy Sources

The Honeybee Standard Brain registry includes the FU Berlin gray-value stacks,
label-field TIFFs, VRML atlas/neuron/tract archives, and neuropil abbreviation
HTML:

- [Virtual Honeybee Standard Brain](https://www.bcp.fu-berlin.de/en/biologie/arbeitsgruppen/neurobiologie/ag_menzel/beebrain/index.html)
- DOI: `10.1002/cne.20644`

Parsed anatomy artifacts include:

- `AtlasDownloadRecord`: local path, download status, size, checksum, error.
- `AtlasInventory`: ZIP file inventory, suffix counts, TIFF count, VRML count,
  image shape, VRML vertex count, and VRML face count.
- `NeuropilAbbreviation`: abbreviation, label, side, and region class.
- `BeeBrainAnatomySummary`: asset count, downloaded count, neuropil coverage,
  bilateral pair count, VRML/TIFF counts, and uncompressed size.

## Activity Sources

The activity pipeline covers all curated BeeBrain activity datasets:

- Paoli 2024 Dryad antennal-lobe calcium `.mat` archives.
- Carcaud 2022 Dryad multisite GCaMP workbooks.
- Andreu 2025 Dryad odorant-receptor alarm-pheromone workbooks.
- Jernigan 2026 Dryad antennal active-sensing CSV archives.
- Nouvian Dryad brain biogenic-amine and cooperative-defence spreadsheets.
- Hadjitofi and Webb 2024 Figshare waggle-following antennal-position CSVs
  ([dataset DOI `10.6084/m9.figshare.24715977.v1`](https://figshare.com/articles/dataset/Honeybee_antennal_positioning_data_when_following_dances/24715977)).

Parsed activity artifacts include:

- `EmpiricalCalciumDataset`
- `EmpiricalOdorResponsePanel`
- `AntennalMovementSummary`
- `EmpiricalWaggleFollowerDataset`
- `WaggleFollowerTrack`
- `WaggleFollowerSummary`
- `BeeBrainDataCompletenessPanel`
- `BeeBrainSourceGap`
- `BeeBrainSourceStatus`
- `EmpiricalTemplateBank`
- `BeeBrainActivitySummary`
- `BeeBrainEndToEndReport`

## Analysis Outputs

`scripts/analyze_empirical_bee_data.py` writes:

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

## Fidelity Notes

This is an empirical-data pipeline, not a full connectome simulator. It
downloads and parses public honeybee anatomy/activity payloads where upstream
access allows it. It then projects those data into reduced BeeBrain contracts:
odor templates, calcium summaries, antennal vibration drive, waggle-follower
decoding confidence, neuropil coverage, and region response summaries. Missing
or blocked files are reported as gaps.

The current configured gate is `brain_data_parseable_fraction >= 0.5`, set by
`research.empirical_completeness_threshold` in `manuscript/config.yaml`. The
stricter `0.800` parseability target remains an improvement target. When a
source cannot yet be parsed locally, the completeness panel can still pass the
readiness gate only if the source is DOI/source-verified and the manifest
records the precise blocker, parser status, and remediation path. This is how
large or access-restricted sources such as Paoli calcium traces remain visible
without being replaced by fabricated traces.
