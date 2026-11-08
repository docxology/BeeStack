"""Workbook and CSV odor-response panel loaders."""

from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from openpyxl import load_workbook

from ...security import validate_zip_archive_bounds
from ..empirical_data import EmpiricalOdorResponsePanel, parse_tabular_odor_response_rows
from .common import (
    dataset_id_from_path,
    first_text_value,
    iter_xlsx_members,
    numeric,
    receptor_from_name,
    trim_empty_rows,
    units_from_sheet,
    validate_workbook,
    workbook_bytes,
)
from .nouvian import nouvian_rows_from_sheet


def load_empirical_panels(source_dir: Path) -> tuple[EmpiricalOdorResponsePanel, ...]:
    panels: list[EmpiricalOdorResponsePanel] = []
    for zip_path in sorted(source_dir.glob("*/*.zip")):
        dataset_id = zip_path.parent.name
        with zipfile.ZipFile(zip_path) as archive:
            validate_zip_archive_bounds(archive)
            for name, data in iter_xlsx_members(archive):
                panels.extend(panels_from_workbook(dataset_id, name, data))
    for zip_path in sorted(source_dir.glob("*/files/**/*.zip")):
        dataset_id = dataset_id_from_path(source_dir, zip_path)
        with zipfile.ZipFile(zip_path) as archive:
            validate_zip_archive_bounds(archive)
            for name, data in iter_xlsx_members(archive):
                panels.extend(panels_from_workbook(dataset_id, name, data))
    for workbook_path in sorted(source_dir.glob("*/files/**/*.xlsx")):
        dataset_id = dataset_id_from_path(source_dir, workbook_path)
        panels.extend(
            panels_from_workbook(dataset_id, workbook_path.name, workbook_bytes(workbook_path))
        )
    for workbook_path in sorted(source_dir.glob("*/*.xlsx")):
        dataset_id = workbook_path.parent.name
        panels.extend(
            panels_from_workbook(dataset_id, workbook_path.name, workbook_bytes(workbook_path))
        )
    return tuple(panels)


def workbook_dataframe_summaries(source_dir: Path) -> list[dict[str, int | float | str]]:
    summaries: list[dict[str, int | float | str]] = []
    for zip_path in sorted(source_dir.glob("*/*.zip")):
        dataset_id = zip_path.parent.name
        with zipfile.ZipFile(zip_path) as archive:
            validate_zip_archive_bounds(archive)
            for name, data in iter_xlsx_members(archive):
                summaries.extend(dataframe_summaries_from_workbook(dataset_id, name, data))
    for zip_path in sorted(source_dir.glob("*/files/**/*.zip")):
        dataset_id = dataset_id_from_path(source_dir, zip_path)
        with zipfile.ZipFile(zip_path) as archive:
            validate_zip_archive_bounds(archive)
            for name, data in iter_xlsx_members(archive):
                summaries.extend(dataframe_summaries_from_workbook(dataset_id, name, data))
    for workbook_path in sorted(source_dir.glob("*/files/**/*.xlsx")):
        dataset_id = dataset_id_from_path(source_dir, workbook_path)
        summaries.extend(
            dataframe_summaries_from_workbook(
                dataset_id, workbook_path.name, workbook_bytes(workbook_path)
            )
        )
    for workbook_path in sorted(source_dir.glob("*/*.xlsx")):
        dataset_id = workbook_path.parent.name
        summaries.extend(
            dataframe_summaries_from_workbook(
                dataset_id, workbook_path.name, workbook_bytes(workbook_path)
            )
        )
    return summaries


def panels_from_workbook(
    dataset_id: str, workbook_name: str, data: bytes
) -> list[EmpiricalOdorResponsePanel]:
    panels: list[EmpiricalOdorResponsePanel] = []
    validate_workbook(data)
    workbook = load_workbook(BytesIO(data), read_only=True, data_only=True)
    try:
        receptor = receptor_from_name(workbook_name)
        workbook_basename = Path(workbook_name).name
        for sheet in workbook.worksheets:
            rows = [tuple(cell for cell in row) for row in sheet.iter_rows(values_only=True)]
            table = trim_empty_rows(rows)
            if len(table) < 2:
                continue
            first_header = str(table[0][0] or "").strip().lower()
            if first_header == "frames":
                rows_for_panel = timecourse_rows(sheet.title, table, receptor)
                modality = f"{workbook_name}:{sheet.title}:timecourse_peak"
            elif first_header.startswith("bees"):
                rows_for_panel = stimulus_by_bee_rows(table)
                modality = f"{workbook_name}:{sheet.title}:regional_intensity"
            elif first_header.startswith("individual"):
                rows_for_panel = individual_by_stimulus_rows(table, receptor or sheet.title)
                modality = f"{workbook_name}:{sheet.title}:receptor_response"
            elif workbook_basename.lower().startswith("data "):
                rows_for_panel = nouvian_rows_from_sheet(workbook_name, sheet.title, table)
                modality = f"{workbook_name}:{sheet.title}:nouvian_structured_response"
            else:
                rows_for_panel = generic_numeric_rows(table, receptor or sheet.title)
                modality = f"{workbook_name}:{sheet.title}:generic_numeric_response"
            if not rows_for_panel:
                continue
            panel = parse_tabular_odor_response_rows(
                dataset_id,
                rows_for_panel,
                stimulus_key="stimulus",
                response_key="response",
                channel_key="channel",
                modality=modality,
                units="pg/ul"
                if "hplc" in f"{workbook_basename}:{sheet.title}".lower()
                and workbook_basename.lower().startswith("data ")
                else units_from_sheet(sheet.title),
            )
            panels.append(panel)
    finally:
        workbook.close()
    return panels


def dataframe_summaries_from_workbook(
    dataset_id: str,
    workbook_name: str,
    data: bytes,
) -> list[dict[str, int | float | str]]:
    summaries: list[dict[str, int | float | str]] = []
    validate_workbook(data)
    sheets = pd.read_excel(BytesIO(data), sheet_name=None, header=None)
    for sheet_name, frame in sheets.items():
        frame = frame.dropna(how="all").dropna(axis=1, how="all")
        if frame.empty:
            continue
        numeric_frame = frame.apply(pd.to_numeric, errors="coerce")
        numeric_values = numeric_frame.to_numpy(dtype=float, copy=False)
        finite_numeric = np.isfinite(numeric_values)
        summaries.append(
            {
                "dataset_id": dataset_id,
                "workbook": workbook_name,
                "sheet": str(sheet_name),
                "row_count": int(frame.shape[0]),
                "column_count": int(frame.shape[1]),
                "numeric_cell_count": int(finite_numeric.sum()),
                "finite_numeric_fraction": float(finite_numeric.mean())
                if numeric_values.size
                else 0.0,
            }
        )
    return summaries


def _table_headers(table: list[tuple[Any, ...]]) -> list[str]:
    headers = [str(cell).strip() if cell is not None else "" for cell in table[0]]
    named_headers = [header for header in headers[1:] if header]
    if len(named_headers) != len(set(named_headers)):
        raise ValueError("ambiguous duplicate response headers")
    if any(
        not header and any(numeric(row[index]) is not None for row in table[1:] if index < len(row))
        for index, header in enumerate(headers[1:], start=1)
    ):
        raise ValueError("numeric responses require named columns")
    return headers


def stimulus_by_bee_rows(table: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    headers = _table_headers(table)
    rows: list[dict[str, Any]] = []
    for row in table[1:]:
        stimulus = row[0]
        if stimulus in (None, ""):
            continue
        for index, channel in enumerate(headers[1:], start=1):
            if not channel:
                continue
            value = row[index] if index < len(row) else None
            rows.append({"stimulus": str(stimulus), "channel": channel, "response": value})
    return rows


def individual_by_stimulus_rows(
    table: list[tuple[Any, ...]], channel_prefix: str
) -> list[dict[str, Any]]:
    headers = _table_headers(table)
    rows: list[dict[str, Any]] = []
    for row in table[1:]:
        individual = str(row[0]).strip() if row and row[0] is not None else ""
        if not individual:
            continue
        for index, stimulus in enumerate(headers[1:], start=1):
            if not stimulus:
                continue
            value = row[index] if index < len(row) else None
            rows.append(
                {
                    "stimulus": stimulus,
                    "channel": f"{channel_prefix}:{individual}",
                    "response": value,
                }
            )
    return rows


def timecourse_rows(
    sheet_name: str, table: list[tuple[Any, ...]], channel_prefix: str | None
) -> list[dict[str, Any]]:
    headers = _table_headers(table)
    rows: list[dict[str, Any]] = []
    for row in table[1:]:
        if numeric(row[0] if row else None) is None and any(
            numeric(cell) is not None for cell in row[1:]
        ):
            raise ValueError("timecourse responses require numeric frame labels")
    for index, stimulus in enumerate(headers[1:], start=1):
        if not stimulus:
            continue
        values: list[float] = []
        for row in table[1:]:
            raw_value = row[index] if index < len(row) else None
            value = numeric(raw_value)
            if value is None:
                if raw_value not in (None, "", "NA"):
                    raise ValueError("timecourse observations must be finite numbers")
                continue
            values.append(abs(value))
        rows.append(
            {
                "stimulus": stimulus,
                "channel": f"{channel_prefix or 'timecourse'}:{sheet_name}",
                "response": max(values) if values else None,
            }
        )
    return rows


def generic_numeric_rows(table: list[tuple[Any, ...]], channel_prefix: str) -> list[dict[str, Any]]:
    headers = _table_headers(table)
    response_columns = [
        index
        for index, header in enumerate(headers)
        if header and any(numeric(row[index]) is not None for row in table[1:] if index < len(row))
    ]
    rows: list[dict[str, Any]] = []
    for row in table[1:]:
        stimulus = first_text_value(tuple(cell for cell in row if isinstance(cell, str)))
        if stimulus is None:
            return []
        for index in response_columns:
            value = row[index] if index < len(row) else None
            channel = headers[index]
            rows.append(
                {
                    "stimulus": stimulus,
                    "channel": f"{channel_prefix}:{channel}",
                    "response": value,
                }
            )
    stimulus_count = len({row["stimulus"] for row in rows})
    channel_count = len({row["channel"] for row in rows})
    return rows if stimulus_count >= 2 and channel_count >= 1 else []
