"""Shared metadata sidecars for BeeStack figure outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypedDict, cast

from PIL import Image, ImageStat

from ..utils import project_relative_path
from .figure_registry import figure_narrative_for_path, generic_figure_sidecar_fields
from .style import wcag_contrast_check


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
    caption: str | None = None,
    alt_text: str | None = None,
    manuscript_section: str | None = None,
    manuscript_label: str | None = None,
    claim_tier: str | None = None,
    citation_keys: tuple[str, ...] = (),
    source_dois: tuple[str, ...] = (),
    accessibility_checks: dict[str, Any] | None = None,
    design_citation_keys: tuple[str, ...] = (),
    design_source_dois: tuple[str, ...] = (),
    unsupported_inference: str | None = None,
    priority: str | None = None,
    artifact_kind: str = "figure",
) -> Path:
    """Write a JSON sidecar describing figure provenance and validation."""

    quality = assert_nonblank_quality(path)
    narrative = figure_narrative_for_path(path)
    narrative_fields = (
        narrative.as_sidecar_fields()
        if narrative
        else generic_figure_sidecar_fields(
            path,
            title=title,
            fidelity=fidelity,
            source_data=source_data,
            regeneration_command=regeneration_command,
        )
    )
    payload: dict[str, Any] = {
        "schema": "beestack.figure.v1",
        "figure_path": project_relative_path(path),
        "title": title,
        "backend": backend,
        "fidelity": fidelity,
        "source_data": project_relative_path(source_data),
        "validation_status": validation_status,
        "regeneration_command": regeneration_command,
        "quality": quality,
        "accessibility_checks": accessibility_checks or wcag_contrast_check(),
    }
    payload.update(narrative_fields)
    overrides: dict[str, object | None] = {
        "caption": caption,
        "alt_text": alt_text,
        "manuscript_section": manuscript_section,
        "manuscript_label": manuscript_label,
        "claim_tier": claim_tier,
        "unsupported_inference": unsupported_inference,
        "priority": priority,
        "artifact_kind": artifact_kind,
    }
    payload.update({key: value for key, value in overrides.items() if value is not None})
    if citation_keys:
        payload["citation_keys"] = citation_keys
    if source_dois:
        payload["source_dois"] = source_dois
    if design_citation_keys:
        payload["design_citation_keys"] = design_citation_keys
    if design_source_dois:
        payload["design_source_dois"] = design_source_dois
    if metrics:
        payload["metrics"] = metrics
    sidecar = path.with_suffix(".json")
    sidecar.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return sidecar
