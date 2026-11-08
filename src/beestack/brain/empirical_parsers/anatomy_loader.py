"""Honeybee Standard Brain anatomy loader."""

from __future__ import annotations

import json
from pathlib import Path

from ..anatomy import (
    AtlasDownloadRecord,
    AtlasInventory,
    BeeBrainAnatomySummary,
    NeuropilAbbreviation,
    atlas_download_record_from_asset,
    atlas_inventories_from_directory,
    load_neuropil_abbreviations,
    summarize_anatomy,
)
from ..datasets import empirical_anatomy_datasets


def load_anatomy(
    source_dir: Path,
) -> tuple[
    BeeBrainAnatomySummary,
    tuple[AtlasInventory, ...],
    tuple[NeuropilAbbreviation, ...],
    tuple[AtlasDownloadRecord, ...],
]:
    records = tuple(
        atlas_download_record_from_asset(
            dataset.dataset_id, asset, source_dir / dataset.dataset_id / asset.file_name
        )
        for dataset in empirical_anatomy_datasets()
        for asset in dataset.assets
    )
    atlas_dir = source_dir / "virtual-honeybee-standard-brain"
    inventories = atlas_inventories_from_directory(atlas_dir) if atlas_dir.exists() else ()
    abbreviations = load_neuropil_abbreviations(atlas_dir / "neuropil_abbreviations.html")
    summary = summarize_anatomy(records, inventories, abbreviations)
    return summary, inventories, abbreviations, records


def json_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or any(not isinstance(row, dict) for row in payload):
        raise ValueError(f"{path.name} must contain a list of object records")
    return [dict(row) for row in payload]
