"""Serializable plot inputs for BeeStack figure outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..utils import project_relative_path, project_relative_payload

FIGURE_DATA_SCHEMA = "beestack.figure_data.v1"


def figure_data_path(path: Path) -> Path:
    """Return the canonical raw-data sidecar path for a rendered figure."""

    return path.with_name(f"{path.stem}_data.json")


def write_figure_plot_data(path: Path, payload: dict[str, Any]) -> Path:
    """Write plottable series or schematic structure for one figure."""

    data_path = figure_data_path(path)
    normalized = project_relative_payload(payload)
    body = {"schema": FIGURE_DATA_SCHEMA, "figure_path": project_relative_path(path), **normalized}
    data_path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data_path


def timeseries_plot(
    *,
    title: str,
    x_key: str,
    x: list[float] | list[int],
    series: dict[str, list[float]],
    chart_type: str = "timeseries",
) -> dict[str, Any]:
    """Build a multi-series time/step plot payload."""

    return {
        "chart_type": chart_type,
        "title": title,
        "x_key": x_key,
        "x": x,
        "series": series,
    }


def categorical_plot(
    *,
    title: str,
    labels: list[str],
    values: list[float],
    orientation: str = "horizontal",
    chart_type: str = "bar",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a categorical bar chart payload."""

    payload: dict[str, Any] = {
        "chart_type": chart_type,
        "title": title,
        "orientation": orientation,
        "labels": labels,
        "values": values,
    }
    if extra:
        payload.update(extra)
    return payload


def heatmap_plot(
    *,
    title: str,
    row_labels: list[str],
    column_labels: list[str],
    matrix: list[list[float]],
    value_label: str,
) -> dict[str, Any]:
    """Build a matrix heatmap payload."""

    return {
        "chart_type": "heatmap",
        "title": title,
        "row_labels": row_labels,
        "column_labels": column_labels,
        "matrix": matrix,
        "value_label": value_label,
    }


def polar_plot(
    *,
    title: str,
    labels: list[str],
    angles_deg: list[float],
) -> dict[str, Any]:
    """Build a polar scatter/phase plot payload."""

    return {
        "chart_type": "polar",
        "title": title,
        "labels": labels,
        "angles_deg": angles_deg,
    }


def schematic_plot(
    *,
    title: str,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]] | None = None,
    annotations: list[str] | None = None,
    rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a non-numeric schematic or audit-table payload."""

    payload: dict[str, Any] = {
        "chart_type": "schematic",
        "title": title,
        "nodes": nodes,
    }
    if edges:
        payload["edges"] = edges
    if annotations:
        payload["annotations"] = annotations
    if rows:
        payload["rows"] = rows
    return payload


def contact_sheet_plot(
    *,
    title: str,
    source_gif: str,
    frame_count: int,
    sampled_frame_indices: list[int],
    columns: int = 4,
) -> dict[str, Any]:
    """Build metadata for animation contact-sheet stills."""

    return {
        "chart_type": "contact_sheet",
        "title": title,
        "source_gif": source_gif,
        "frame_count": frame_count,
        "sampled_frame_indices": sampled_frame_indices,
        "columns": columns,
    }
