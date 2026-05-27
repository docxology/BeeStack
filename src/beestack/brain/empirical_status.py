"""Catalog and parser status helpers for empirical completeness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .anatomy import BeeBrainAnatomySummary
from .empirical_data import (
    AntennalMovementSummary,
    EmpiricalCalciumDataset,
    EmpiricalOdorResponsePanel,
    EmpiricalWaggleFollowerDataset,
    SzyszkaGrangerSupplementSummary,
)
from .empirical_parsers.anatomy_loader import json_rows


def archive_status(source_dir: Path) -> list[dict[str, Any]]:
    path = source_dir / "archives.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def catalog_status(source_dir: Path) -> list[dict[str, Any]]:
    return json_rows(source_dir / "catalog.json")


def anatomy_download_status(source_dir: Path) -> list[dict[str, Any]]:
    return json_rows(source_dir / "anatomy_downloads.json")


def downloaded_dataset_ids(
    archive_rows: list[dict[str, Any]],
    catalog_rows: list[dict[str, Any]],
    anatomy_rows: list[dict[str, Any]],
) -> set[str]:
    ids = {
        str(row.get("dataset_id"))
        for row in archive_rows
        if row.get("archive_downloaded") or int(row.get("file_downloaded_count") or 0) > 0
    }
    ids.update(str(row.get("dataset_id")) for row in catalog_rows if row.get("file_downloaded"))
    ids.update(str(row.get("dataset_id")) for row in anatomy_rows if row.get("downloaded"))
    return {dataset_id for dataset_id in ids if dataset_id and dataset_id != "None"}


def parseable_dataset_ids(
    panels: tuple[EmpiricalOdorResponsePanel, ...],
    calcium_datasets: tuple[EmpiricalCalciumDataset, ...],
    antennal_summaries: tuple[AntennalMovementSummary, ...],
    waggle_dataset: EmpiricalWaggleFollowerDataset | None,
    anatomy_summary: BeeBrainAnatomySummary,
    szyszka_supplement: SzyszkaGrangerSupplementSummary | None = None,
) -> set[str]:
    ids = {panel.dataset_id for panel in panels}
    ids.update(dataset.dataset_id for dataset in calcium_datasets)
    ids.update(summary.dataset_id for summary in antennal_summaries)
    if waggle_dataset is not None:
        ids.add(waggle_dataset.dataset_id)
    if anatomy_summary.inventory_count or anatomy_summary.neuropil_count:
        ids.add(anatomy_summary.dataset_id)
    if szyszka_supplement is not None:
        ids.add(szyszka_supplement.dataset_id)
    return ids


def parser_status_by_dataset(
    catalog_rows: list[dict[str, Any]],
    parseable_ids: set[str],
) -> dict[str, str]:
    statuses: dict[str, str] = {dataset_id: "parsed" for dataset_id in parseable_ids}
    for row in catalog_rows:
        dataset_id = str(row.get("dataset_id") or "")
        if not dataset_id or statuses.get(dataset_id) == "parsed":
            continue
        parser_status = str(row.get("parser_status") or "")
        file_error = str(row.get("file_error") or "")
        if file_error:
            statuses[dataset_id] = f"download_blocked:{file_error}"
        elif parser_status.startswith("citation_anchor_only") or parser_status and parser_status_priority(parser_status) > parser_status_priority(
            statuses.get(dataset_id, "")
        ):
            statuses[dataset_id] = parser_status
    return statuses


def parser_status_priority(status: str) -> int:
    if status.startswith("download_blocked:"):
        return 100
    if status.startswith("supported_"):
        return 80
    if status.startswith("metadata_"):
        return 20
    if status.startswith("citation_anchor_only"):
        return 15
    if status:
        return 10
    return 0


def known_gaps(
    archive_rows: list[dict[str, Any]],
    anatomy_summary: BeeBrainAnatomySummary,
    activity_summary: Any,
    waggle_dataset: EmpiricalWaggleFollowerDataset | None = None,
) -> list[str]:
    gaps: list[str] = []
    for row in archive_rows:
        if not row.get("archive_downloaded") and int(row.get("file_downloaded_count") or 0) == 0:
            gaps.append(
                f"{row.get('dataset_id')} cataloged but no archive or file-level payload is local"
            )
    if anatomy_summary.downloaded_asset_count < anatomy_summary.asset_count:
        gaps.append("some Honeybee Standard Brain anatomy assets are cataloged but not local")
    if activity_summary.calcium_dataset_count == 0:
        gaps.append("Paoli MATLAB calcium traces are not yet local or parseable")
    if anatomy_summary.neuropil_count == 0:
        gaps.append("neuropil abbreviation HTML is not yet local or parseable")
    if waggle_dataset is None:
        gaps.append("Hadjitofi-Webb Figshare waggle-following CSVs are not yet local or parseable")
    return gaps
