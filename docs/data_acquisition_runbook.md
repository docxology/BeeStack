# Data Acquisition Runbook

BeeStack treats empirical raw data as regeneratable output. The source code
contains registries, typed records, parsers, and tests; downloaded archives stay
under `output/data/empirical_sources/`.

## Default Full Download

```bash
uv run python scripts/fetch_empirical_bee_data.py
```

Default behavior:

- catalog every curated Dryad BeeBrain activity dataset;
- attempt each Dryad version archive first;
- if an archive endpoint fails, attempt cataloged file-level downloads;
- catalog and download the CC BY 4.0 Hadjitofi-Webb Figshare waggle-following
  CSV files through the Figshare article API;
- download Honeybee Standard Brain anatomy assets from FU Berlin;
- skip only completion-verified caches bound to the original source identity;
- record byte count, checksum, source identity, and completion status;
- record upstream errors in JSON instead of hiding them.

## Metadata-Only Mode

```bash
uv run python scripts/fetch_empirical_bee_data.py --metadata-only
```

Use this when you need catalogs and source manifests but do not want to transfer
large payloads.

## Force Refresh

```bash
uv run python scripts/fetch_empirical_bee_data.py --force
```

Use this when local files are stale, incomplete, or deliberately being revalidated.
Normal operation skips only verified completion receipts; nonempty bytes alone do
not establish completion or bind a failed refresh to a new DOI/version.

## Manifests

- `output/data/empirical_sources/catalog.json`: Dryad and Figshare file catalog
  with local file paths, archive status, parser status, file-level errors, and
  checksums.
- `output/data/empirical_sources/archives.json`: one row per Dryad dataset with
  archive size, archive checksum, error state, and file-fallback counts.
- `output/data/empirical_sources/anatomy_downloads.json`: one row per Honeybee
  Standard Brain asset with local path, checksum, asset type, and error state.

## Data Size Caveats

Dryad archives can be hundreds of megabytes. Do not commit raw archives. Retain
them and their completion records under `output/data/empirical_sources/`; upstream
availability is not guaranteed, so reacquisition is not a safe cleanup substitute.
Some upstream endpoints may reject unauthenticated archive downloads. When that
happens, BeeStack records the HTTP response and tries file-level URLs where
available.
Downloads and container intake are bounded before expansion/materialization. The
budget contracts in `security_posture.md` cover transfer bytes, archive trees,
workbook cells, derived channel × stimulus odor panels, and MATLAB/HDF5 arrays/
graphs. HDF5 external raw storage and virtual layouts refuse alongside external
links: a sealed container alone cannot seal those dependencies. A policy refusal
remains a blocker, never a successful empty parse or permission to bypass limits.

## After Download

```bash
uv run python scripts/analyze_empirical_bee_data.py
uv run python scripts/analysis_pipeline.py
uv run python scripts/z_generate_manuscript_variables.py
```

The aggregate requires at least one parseable odor-response panel. Standalone
waggle or supplementary-statistics parsers may have local inputs without enabling
the odor-conditioned aggregate. Skips/failures retain historical outputs but
invalidate current evidence; a successful stage binds raw payloads, configuration,
implementation, and report hashes. Missing observations remain unavailable.
