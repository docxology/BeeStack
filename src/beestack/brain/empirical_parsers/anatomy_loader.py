"""Honeybee Standard Brain anatomy loader."""

from __future__ import annotations

import json
from pathlib import Path

from ..anatomy import (
    AtlasDownloadRecord,
    AtlasInventory,
    BeeBrainAnatomySummary,
    NeuropilAbbreviation,
    atlas_download_records_from_dicts,
    atlas_inventories_from_directory,
    load_neuropil_abbreviations,
    summarize_anatomy,
)


def load_anatomy(
    source_dir: Path,
) -> tuple[
    BeeBrainAnatomySummary,
    tuple[AtlasInventory, ...],
    tuple[NeuropilAbbreviation, ...],
    tuple[AtlasDownloadRecord, ...],
]:
    rows = json_rows(source_dir / "anatomy_downloads.json")
    records = atlas_download_records_from_dicts(tuple(rows))
    atlas_dir = source_dir / "virtual-honeybee-standard-brain"
    inventories = atlas_inventories_from_directory(atlas_dir) if atlas_dir.exists() else ()
    abbreviations = load_neuropil_abbreviations(atlas_dir / "neuropil_abbreviations.html")
    summary = summarize_anatomy(records, inventories, abbreviations)
    return summary, inventories, abbreviations, records


def json_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [dict(row) for row in payload] if isinstance(payload, list) else []
