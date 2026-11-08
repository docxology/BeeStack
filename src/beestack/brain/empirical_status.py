"""Catalog and parser status helpers for empirical completeness."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ..config import BeeStackConfig
from ..security import completed_download, completion_path
from ..security.path_safety import download_source_identity
from ..utils import read_json
from .anatomy import BeeBrainAnatomySummary
from .empirical_data import (
    AntennalMovementSummary,
    EmpiricalCalciumDataset,
    EmpiricalOdorResponsePanel,
    EmpiricalWaggleFollowerDataset,
    SzyszkaGrangerSupplementSummary,
)
from .empirical_parsers.anatomy_loader import json_rows


def _local_payload_path(
    source_dir: Path, dataset_id: object, raw_path: object, project_root: Path | None
) -> Path | None:
    if (
        not isinstance(dataset_id, str)
        or not dataset_id
        or Path(dataset_id).name != dataset_id
        or dataset_id in {".", ".."}
    ):
        return None
    if not isinstance(raw_path, str) or not raw_path:
        return None
    path = Path(raw_path)
    if not path.is_absolute():
        if project_root is None:
            return None
        path = project_root / path
    try:
        dataset_dir = (source_dir / dataset_id).resolve()
        resolved_path = path.resolve()
        if not dataset_dir.is_relative_to(source_dir.resolve()) or not resolved_path.is_relative_to(
            dataset_dir
        ):
            return None
        return path
    except (OSError, ValueError, RuntimeError):
        return None


def _verified_local_payload(
    source_dir: Path,
    dataset_id: object,
    raw_path: object,
    project_root: Path | None,
    *,
    source_identity: str | None,
) -> Path | None:
    path = _local_payload_path(source_dir, dataset_id, raw_path, project_root)
    if path is None or source_identity is None:
        return None
    return path.resolve() if completed_download(path, source_identity=source_identity) else None


def _file_source_identity(row: dict[str, Any]) -> str | None:
    url = row.get("download_url")
    if not isinstance(url, str) or not url:
        return None
    try:
        return download_source_identity(url, doi=row.get("doi"), size=row.get("size"))
    except (ValueError, TypeError):
        return None


def _archive_source_identity(row: dict[str, Any]) -> str | None:
    url = row.get("archive_download_url")
    if not isinstance(url, str) or not url:
        return None
    try:
        return download_source_identity(
            url, doi=row.get("doi"), size=row.get("archive_expected_size_bytes")
        )
    except (ValueError, TypeError):
        return None


def archive_status(source_dir: Path, *, project_root: Path | None = None) -> list[dict[str, Any]]:
    rows = json_rows(source_dir / "archives.json")
    verified_catalog: set[tuple[str, Path]] = set()
    for entry in catalog_status(source_dir, project_root=project_root):
        if entry["file_downloaded"]:
            path = _local_payload_path(
                source_dir, entry.get("dataset_id"), entry.get("local_file"), project_root
            )
            if path is not None:
                verified_catalog.add((str(entry["dataset_id"]), path.resolve()))
    for row in rows:
        dataset_id = row.get("dataset_id")
        row["archive_downloaded"] = bool(
            _verified_local_payload(
                source_dir,
                dataset_id,
                row.get("local_archive"),
                project_root,
                source_identity=_archive_source_identity(row),
            )
        )
        paths = row.get("downloaded_file_paths") or []
        if not isinstance(paths, list) or any(not isinstance(path, str) for path in paths):
            raise ValueError("downloaded_file_paths must be a list of paths")
        verified_files: dict[Path, str] = {}
        for path in paths:
            verified = _local_payload_path(source_dir, dataset_id, path, project_root)
            if verified is not None and (str(dataset_id), verified.resolve()) in verified_catalog:
                verified_files.setdefault(verified.resolve(), path)
        row["downloaded_file_paths"] = list(verified_files.values())
        row["file_downloaded_count"] = len(row["downloaded_file_paths"])
        if not row["archive_downloaded"]:
            row["archive_sha256"] = None
            row["archive_size_bytes"] = None
    return rows


def catalog_status(source_dir: Path, *, project_root: Path | None = None) -> list[dict[str, Any]]:
    rows = json_rows(source_dir / "catalog.json")
    for row in rows:
        row["file_downloaded"] = bool(
            _verified_local_payload(
                source_dir,
                row.get("dataset_id"),
                row.get("local_file"),
                project_root,
                source_identity=_file_source_identity(row),
            )
        )
        row["archive_downloaded"] = bool(
            _verified_local_payload(
                source_dir,
                row.get("dataset_id"),
                row.get("local_archive"),
                project_root,
                source_identity=_archive_source_identity(row),
            )
        )
        if not row["file_downloaded"]:
            row["file_sha256"] = None
    return rows


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
        elif (
            parser_status.startswith("citation_anchor_only")
            or parser_status
            and parser_status_priority(parser_status)
            > parser_status_priority(statuses.get(dataset_id, ""))
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


def _current_file_sha256(path: Path) -> str:
    before = path.stat()
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    after = path.stat()
    fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in fields):
        raise ValueError("empirical evidence changed while being read")
    return digest


def empirical_input_paths(project_root: Path) -> tuple[Path, ...]:
    """Raw inputs and acquisition metadata, excluding unsealed generated guides."""
    root = project_root.resolve()
    source = root / "output/data/empirical_sources"
    if not source.exists():
        return ()
    if source.is_symlink() or not source.resolve().is_relative_to(root):
        raise ValueError("empirical input tree must remain inside the project")
    paths = []
    for path in source.rglob("*"):
        if path.is_symlink():
            raise ValueError("linked empirical inputs cannot certify current analysis")
        if not path.is_file():
            continue
        if path.name in {"README.md", "AGENTS.md"} and not completion_path(path).is_file():
            continue
        paths.append(path)
    return tuple(sorted(paths))


def empirical_inputs_sha256(project_root: Path) -> dict[str, str]:
    root = project_root.resolve()
    return {
        path.relative_to(root).as_posix(): _current_file_sha256(path)
        for path in empirical_input_paths(root)
    }


def empirical_implementation_sha256() -> dict[str, str]:
    package = Path(__file__).resolve().parents[1]
    return {
        path.relative_to(package).as_posix(): _current_file_sha256(path)
        for path in sorted(package.rglob("*.py"))
    }


def empirical_configuration_sha256(cfg: BeeStackConfig) -> str:
    encoded = json.dumps(asdict(cfg), sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def current_empirical_analysis(project_root: Path, cfg: BeeStackConfig) -> dict[str, Any]:
    """Require unchanged raw inputs, implementation, configuration and report bytes."""

    data_dir = project_root / "output/data"
    reason = "No fresh odor-response panel analysis; retained empirical artifacts are historical, not current observations."
    try:
        availability = read_json(data_dir / "empirical_availability.json")
        if (
            isinstance(availability, dict)
            and availability.get("scope") == "odor_response_panel_analysis"
            and availability.get("current") is True
            and availability.get("configuration_sha256") == empirical_configuration_sha256(cfg)
            and bool(availability.get("input_sha256"))
            and availability.get("input_sha256") == empirical_inputs_sha256(project_root)
            and availability.get("implementation_sha256") == empirical_implementation_sha256()
        ):
            raw = (data_dir / "empirical_analysis.json").read_bytes()
            if availability.get("report_sha256") == hashlib.sha256(raw).hexdigest():
                report = json.loads(raw)
                if not isinstance(report, dict):
                    raise ValueError("empirical report must be a JSON object")
                return {**report, "availability_status": "current"}
    except (OSError, ValueError, TypeError) as exc:
        reason = f"Empirical availability could not be verified ({type(exc).__name__}); retained artifacts are historical, not current observations."
    return {"availability_status": "historical_unavailable", "known_gaps": [reason]}
