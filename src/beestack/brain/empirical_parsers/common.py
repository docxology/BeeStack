"""Shared helpers for empirical archive parsing."""

from __future__ import annotations

import zipfile
from csv import DictReader
from io import BytesIO
from pathlib import Path
from typing import Any

from ...security import assert_safe_zip_member, validate_zip_archive_bounds


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in DictReader(handle)]


def dataset_id_from_path(source_dir: Path, path: Path) -> str:
    relative = path.relative_to(source_dir)
    return relative.parts[0]


def iter_xlsx_members(archive: zipfile.ZipFile, prefix: str = ""):
    for info in archive.infolist():
        if info.is_dir():
            continue
        assert_safe_zip_member(info.filename)
        member_name = f"{prefix}{info.filename}"
        data = archive.read(info)
        if info.filename.lower().endswith(".xlsx"):
            yield member_name, data
        elif info.filename.lower().endswith(".zip"):
            with zipfile.ZipFile(BytesIO(data)) as nested:
                validate_zip_archive_bounds(nested)
                yield from iter_xlsx_members(nested, prefix=f"{info.filename}/")


def trim_empty_rows(rows: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    return [row for row in rows if any(cell is not None for cell in row)]


def text(value: Any) -> str:
    return "" if value in (None, "") else str(value).strip()


def numeric(value: Any) -> float | None:
    if value in (None, "", "NA"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def join_label(*parts: str | None) -> str:
    return ":".join(part for part in parts if part)


def first_text_value(row: tuple[Any, ...]) -> str | None:
    for value in row:
        if value in (None, ""):
            continue
        if numeric(value) is None:
            cell = str(value).strip()
            if cell:
                return cell
    return None


def normalize_header(header: str) -> str:
    return " ".join(header.lower().replace("(", " ").replace(")", " ").split()).replace(" ", "_")


def normalize_label(label: str) -> str:
    return " ".join(str(label).replace("_", " ").split()).strip().lower()


def receptor_from_name(name: str) -> str | None:
    lowered = name.lower()
    if "amor109" in lowered:
        return "AmOR109"
    if "amor136" in lowered:
        return "AmOR136"
    return None


def units_from_sheet(sheet_name: str) -> str:
    lowered = sheet_name.lower()
    if "hplc" in lowered:
        return "pg/ul"
    if lowered in {"behaviour", "5ht", "da", "cyp", "flu"}:
        return "attack_or_stinging_probability"
    if "spike" in lowered:
        return "spikes/s"
    if "distance" in lowered:
        return "euclidean distance"
    return "normalized fluorescence"
