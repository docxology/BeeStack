"""Shared helpers for empirical archive parsing."""

from __future__ import annotations

import math
import re
import zipfile
from csv import DictReader
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from ...security import ArchiveBudget, IntakePolicyError


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in DictReader(handle)]


def dataset_id_from_path(source_dir: Path, path: Path) -> str:
    relative = path.relative_to(source_dir)
    return relative.parts[0]


def iter_xlsx_members(
    archive: zipfile.ZipFile,
    prefix: str = "",
    *,
    budget: ArchiveBudget | None = None,
    depth: int = 0,
):
    budget = budget if budget is not None else ArchiveBudget()
    budget.enter(archive, depth)
    for info in archive.infolist():
        if info.is_dir() or not info.filename.lower().endswith((".xlsx", ".zip")):
            continue
        member_name = f"{prefix}{info.filename}"
        budget.consume(info)
        with archive.open(info) as raw:
            data = raw.read(info.file_size + 1)
        if len(data) != info.file_size:
            raise IntakePolicyError("incomplete archive member")
        if info.filename.lower().endswith(".xlsx"):
            validate_workbook(data, budget=budget, depth=depth + 1)
            yield member_name, data
        else:
            with zipfile.ZipFile(BytesIO(data)) as nested:
                yield from iter_xlsx_members(
                    nested, prefix=f"{member_name}/", budget=budget, depth=depth + 1
                )


@dataclass(frozen=True)
class WorkbookLimits:
    max_rows: int = 100_000
    max_columns: int = 4_096
    max_cells: int = 5_000_000
    max_total_cells: int = 10_000_000
    max_package_bytes: int = 256_000_000
    max_member_bytes: int = 128_000_000


def _row_number(value: str, max_rows: int) -> int:
    # XLSX rows have at most seven ASCII digits. Bound syntax before int().
    if len(value) > 7 or re.fullmatch(r"[1-9][0-9]{0,6}", value) is None:
        raise IntakePolicyError("invalid worksheet row")
    row = int(value)
    if row > min(max_rows, 1_048_576):
        raise IntakePolicyError("worksheet exceeds logical row/column/cell cap")
    return row


def _coordinate(value: str, *, limits: WorkbookLimits | None = None) -> tuple[int, int]:
    limits = limits or WorkbookLimits()
    # XFD1048576 is the format maximum: never accumulate arbitrary-length columns.
    if len(value) > 10:
        raise IntakePolicyError("invalid worksheet coordinate")
    match = re.fullmatch(r"([A-Za-z]{1,3})([1-9][0-9]{0,6})", value)
    if match is None:
        raise IntakePolicyError("invalid worksheet coordinate")
    column = 0
    for letter in match[1].upper():
        column = column * 26 + ord(letter) - ord("A") + 1
        if column > min(limits.max_columns, 16_384):
            raise IntakePolicyError("worksheet exceeds logical row/column/cell cap")
    return _row_number(match[2], limits.max_rows), column


def _worksheet_parts(archive: zipfile.ZipFile) -> tuple[zipfile.ZipInfo, ...]:
    """Resolve the same workbook/sheet graph readers use, not a pathname glob."""
    content_ns = "{http://schemas.openxmlformats.org/package/2006/content-types}"
    package_ns = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    sheet_ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    relation_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    workbook_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"
    worksheet_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"
    workbook_types = {
        workbook_type,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.template.main+xml",
        "application/vnd.ms-excel.sheet.macroEnabled.main+xml",
        "application/vnd.ms-excel.template.macroEnabled.main+xml",
    }
    names = archive.namelist()
    if len(names) != len(set(names)):
        raise IntakePolicyError("duplicate workbook package member")
    try:
        content = ElementTree.fromstring(archive.read("[Content_Types].xml"))
        overrides = content.findall(f"{content_ns}Override")
        main = [node for node in content if node.get("ContentType") in workbook_types]
        if (
            len(main) != 1
            or main[0].tag != f"{content_ns}Override"
            or main[0].get("PartName") != "/xl/workbook.xml"
            or main[0].get("ContentType") != workbook_type
        ):
            raise IntakePolicyError("unsupported workbook part location or format")
        content_types = {node.get("PartName"): node.get("ContentType") for node in overrides}
        if len(content_types) != len(overrides):
            raise IntakePolicyError("duplicate workbook content-type override")
        workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        relationships = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        if (
            workbook.tag != f"{sheet_ns}workbook"
            or relationships.tag != f"{package_ns}Relationships"
        ):
            raise IntakePolicyError("unsupported workbook relationship format")
        relations = {}
        worksheet_targets = {}
        for relation in relationships:
            identity = relation.get("Id")
            if relation.tag != f"{package_ns}Relationship" or not identity or identity in relations:
                raise IntakePolicyError("invalid workbook relationship")
            relations[identity] = relation
            if relation.get("Type", "").rsplit("/", 1)[-1] != "worksheet":
                continue
            target = relation.get("Target", "")
            path = target[1:] if target.startswith("/") else f"xl/{target}"
            if (
                relation.get("Type") != f"{relation_ns}/worksheet"
                or relation.get("TargetMode", "Internal") != "Internal"
                or not target
                or any(char in target for char in "\\:%?#")
                or any(ord(char) < 32 for char in target)
                or any(part in {"", ".", ".."} for part in path.split("/"))
                or not path.endswith(".xml")
                or content_types.get(f"/{path}") != worksheet_type
            ):
                raise IntakePolicyError("unsupported worksheet relationship target")
            worksheet_targets[identity] = path
        parts = []
        for sheet in workbook.findall(f"{sheet_ns}sheets/{sheet_ns}sheet"):
            identity = sheet.get(f"{{{relation_ns}}}id")
            if identity not in worksheet_targets:
                raise IntakePolicyError("unsupported worksheet relationship")
            info = archive.getinfo(worksheet_targets[identity])
            if info.is_dir() or info in parts:
                raise IntakePolicyError("invalid or duplicate worksheet part")
            parts.append(info)
        if not parts:
            raise IntakePolicyError("workbook requires worksheet relationships")
        return tuple(parts)
    except (KeyError, ElementTree.ParseError) as error:
        raise IntakePolicyError("invalid workbook package relationships") from error


def validate_workbook(
    data: bytes,
    *,
    limits: WorkbookLimits | None = None,
    budget: ArchiveBudget | None = None,
    depth: int = 0,
) -> None:
    """Preflight package expansion and actual sparse coordinates before either reader."""
    limits = limits or WorkbookLimits()
    budget = budget if budget is not None else ArchiveBudget()
    total_cells = 0
    with zipfile.ZipFile(BytesIO(data)) as archive:
        budget.enter(archive, depth)
        if sum(info.file_size for info in archive.infolist()) > limits.max_package_bytes:
            raise IntakePolicyError("workbook package exceeds expanded byte cap")
        if any(info.file_size > limits.max_member_bytes for info in archive.infolist()):
            raise IntakePolicyError("workbook member exceeds expanded byte cap")
        # Every package member can be read by openpyxl (shared strings/styles too).
        for info in archive.infolist():
            if not info.is_dir():
                budget.consume(info)
        for info in _worksheet_parts(archive):
            max_row = max_column = current_row = current_column = 0
            row_records = cell_records = 0
            stack = []
            with archive.open(info) as raw:
                for event, element in ElementTree.iterparse(raw, events=("start", "end")):
                    tag = element.tag.rsplit("}", 1)[-1]
                    if event == "end":
                        element.clear()
                        stack.pop()
                        if stack:
                            stack[-1].remove(element)
                        continue
                    stack.append(element)
                    if len(stack) > 64:
                        raise IntakePolicyError("worksheet XML exceeds nesting cap")
                    if tag == "dimension":
                        for coord in element.attrib.get("ref", "A1").split(":"):
                            row, column = _coordinate(coord, limits=limits)
                            max_row, max_column = max(max_row, row), max(max_column, column)
                    elif tag == "row":
                        row_records += 1
                        row_attribute = element.attrib.get("r")
                        current_row = (
                            _row_number(row_attribute, limits.max_rows)
                            if row_attribute is not None
                            else current_row + 1
                        )
                        current_column = 0
                        if current_row <= 0:
                            raise IntakePolicyError("invalid worksheet row")
                        max_row = max(max_row, current_row)
                    elif tag == "c":
                        cell_records += 1
                        if "r" in element.attrib:
                            row, column = _coordinate(element.attrib["r"], limits=limits)
                        else:
                            row, column = max(1, current_row), current_column + 1
                        current_column = column
                        max_row, max_column = max(max_row, row), max(max_column, column)
                    if (
                        max_row > min(limits.max_rows, 1_048_576)
                        or max_column > min(limits.max_columns, 16_384)
                        or row_records > limits.max_rows
                        or cell_records > limits.max_cells
                        or max_row * max_column > limits.max_cells
                    ):
                        raise IntakePolicyError("worksheet exceeds logical row/column/cell cap")
            total_cells += max(max_row * max_column, cell_records)
            if total_cells > limits.max_total_cells:
                raise IntakePolicyError("workbook exceeds aggregate logical cell cap")


def workbook_bytes(path: Path) -> bytes:
    with path.open("rb") as raw:
        data = raw.read(512_000_001)
    if len(data) > 512_000_000:
        raise IntakePolicyError("workbook exceeds input byte cap")
    return data


def trim_empty_rows(rows: list[tuple[Any, ...]]) -> list[tuple[Any, ...]]:
    return [row for row in rows if any(cell is not None for cell in row)]


def text(value: Any) -> str:
    return "" if value in (None, "") else str(value).strip()


def numeric(value: Any) -> float | None:
    if isinstance(value, bool) or value in (None, "", "NA"):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


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
