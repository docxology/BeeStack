"""Jernigan antennal movement CSV summaries."""

from __future__ import annotations

import zipfile
from csv import DictReader
from io import BytesIO, TextIOWrapper
from pathlib import Path

from ...security import ArchiveBudget, assert_safe_zip_member, validate_zip_archive_bounds
from ..empirical_data import AntennalMovementSummary, summarize_antennal_movement_rows


def load_antennal_movement_summaries(source_dir: Path) -> tuple[AntennalMovementSummary, ...]:
    summaries: list[AntennalMovementSummary] = []
    for zip_path in sorted(source_dir.glob("*/*.zip")):
        dataset_id = zip_path.parent.name
        with zipfile.ZipFile(zip_path) as archive:
            validate_zip_archive_bounds(archive)
            summaries.extend(antennal_summaries_from_archive(dataset_id, archive))
    required_columns = {"Bee", "Plume", "Frame", "Odor_detector", "LeftTheta", "RightTheta"}
    for csv_path in sorted(source_dir.glob("*/files/**/*.csv")):
        dataset_id = csv_path.parent.parent.name
        with csv_path.open(encoding="utf-8-sig", newline="") as handle:
            rows = DictReader(handle)
            if required_columns <= set(rows.fieldnames or ()):
                summaries.append(summarize_antennal_movement_rows(rows, dataset_id=dataset_id))
    return tuple(summaries)


def antennal_summaries_from_archive(
    dataset_id: str,
    archive: zipfile.ZipFile,
    prefix: str = "",
    *,
    budget: ArchiveBudget | None = None,
    depth: int = 0,
) -> list[AntennalMovementSummary]:
    summaries: list[AntennalMovementSummary] = []
    budget = budget if budget is not None else ArchiveBudget()
    budget.enter(archive, depth)
    required_columns = {"Bee", "Plume", "Frame", "Odor_detector", "LeftTheta", "RightTheta"}
    for info in archive.infolist():
        if info.is_dir():
            continue
        assert_safe_zip_member(info.filename)
        member_name = f"{prefix}{info.filename}"
        lowered = info.filename.lower()
        if lowered.endswith(".csv"):
            budget.consume(info)
            with (
                archive.open(info) as raw,
                TextIOWrapper(raw, encoding="utf-8-sig", newline="") as text,
            ):
                rows = DictReader(text)
                fieldnames = set(rows.fieldnames or ())
                if required_columns <= fieldnames:
                    summaries.append(summarize_antennal_movement_rows(rows, dataset_id=dataset_id))
        elif lowered.endswith(".zip"):
            budget.consume(info)
            with zipfile.ZipFile(BytesIO(archive.read(info))) as nested:
                summaries.extend(
                    antennal_summaries_from_archive(
                        dataset_id, nested, prefix=f"{member_name}/", budget=budget, depth=depth + 1
                    )
                )
    return summaries
