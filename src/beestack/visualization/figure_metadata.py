"""Shared metadata sidecars for BeeStack figure outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypedDict, cast

from PIL import Image, ImageStat


class ImageQualitySummary(TypedDict):
    """Typed image-quality metrics stored in figure sidecars."""

    width_px: int
    height_px: int
    mode: str
    nonzero_histogram_bins: int
    mean_intensity: float
    std_intensity: float
    min_intensity: int
    max_intensity: int


def image_quality_summary(path: Path) -> ImageQualitySummary:
    """Return lightweight, deterministic quality metrics for a rendered figure."""

    with Image.open(path) as image:
        grayscale = image.convert("L")
        histogram = grayscale.histogram()
        stat = ImageStat.Stat(grayscale)
        min_intensity, max_intensity = cast(tuple[int, int], grayscale.getextrema())
        return {
            "width_px": int(image.width),
            "height_px": int(image.height),
            "mode": str(image.mode),
            "nonzero_histogram_bins": int(sum(1 for count in histogram if count)),
            "mean_intensity": float(stat.mean[0]),
            "std_intensity": float(stat.stddev[0]),
            "min_intensity": int(min_intensity),
            "max_intensity": int(max_intensity),
        }


def assert_nonblank_quality(path: Path, *, min_histogram_bins: int = 8) -> ImageQualitySummary:
    """Fail if a figure is empty or visually near-uniform."""

    summary = image_quality_summary(path)
    if int(summary["width_px"]) <= 0 or int(summary["height_px"]) <= 0:
        raise ValueError(f"{path} has invalid dimensions")
    if int(summary["nonzero_histogram_bins"]) < min_histogram_bins:
        raise ValueError(f"{path} appears near-uniform")
    if float(summary["std_intensity"]) <= 0.0:
        raise ValueError(f"{path} appears blank")
    return summary


def write_figure_sidecar(
    path: Path,
    *,
    title: str,
    backend: str,
    fidelity: str,
    source_data: str,
    validation_status: str,
    regeneration_command: str,
    metrics: dict[str, Any] | None = None,
) -> Path:
    """Write a JSON sidecar describing figure provenance and validation."""

    quality = assert_nonblank_quality(path)
    payload: dict[str, Any] = {
        "schema": "beestack.figure.v1",
        "figure_path": str(path),
        "title": title,
        "backend": backend,
        "fidelity": fidelity,
        "source_data": source_data,
        "validation_status": validation_status,
        "regeneration_command": regeneration_command,
        "quality": quality,
    }
    if metrics:
        payload["metrics"] = metrics
    sidecar = path.with_suffix(".json")
    sidecar.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return sidecar
