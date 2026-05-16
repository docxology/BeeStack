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
- skip non-empty local files;
- write checksums for files that are local;
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

Use this only when local files are stale, incomplete, or deliberately being
revalidated. Normal operation should rely on skip-if-present semantics.

## Manifests

- `output/data/empirical_sources/catalog.json`: Dryad and Figshare file catalog
  with local file paths, archive status, parser status, file-level errors, and
  checksums.
- `output/data/empirical_sources/archives.json`: one row per Dryad dataset with
  archive size, archive checksum, error state, and file-fallback counts.
- `output/data/empirical_sources/anatomy_downloads.json`: one row per Honeybee
  Standard Brain asset with local path, checksum, asset type, and error state.

## Data Size Caveats

Dryad archives can be hundreds of megabytes. Do not commit raw archives. They
belong under `output/data/empirical_sources/` and can be regenerated with uv.
Some upstream endpoints may reject unauthenticated archive downloads. When that
happens, BeeStack records the HTTP response and tries file-level URLs where
available.

## After Download

```bash
uv run python scripts/analyze_empirical_bee_data.py
uv run python scripts/analysis_pipeline.py
uv run python scripts/z_generate_manuscript_variables.py
```

The analysis script is tolerant of partial local data. It integrates what is
available, reports missing anatomy/activity/waggle-following gaps, and never
fabricates empirical measurements for unavailable files.
