"""Shared metadata sidecars for BeeStack figure outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypedDict, cast

from PIL import Image, ImageStat

from ..utils import project_relative_path
from .figure_plot_data import write_figure_plot_data
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


class VisualQualitySummary(TypedDict, total=False):
    """Figure-layout metadata consumed by manuscript and gallery audits."""

    width_px: int
    height_px: int
    aspect_ratio: float
    aspect_class: str
    label_density: str
    manuscript_use: str
    min_dimension_px: int
    max_dimension_px: int
    figure_role: str
    split_group: str
    readability_status: str
    readability_exception: str


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


def visual_quality_summary(
    path: Path,
    *,
    quality: ImageQualitySummary | None = None,
    priority: str | None = None,
    manuscript_label: str | None = None,
    artifact_kind: str = "figure",
    claim_tier: str | None = None,
) -> VisualQualitySummary:
    """Return optional layout/readability metadata for rendered figure sidecars."""

    summary = quality or image_quality_summary(path)
    width = int(summary["width_px"])
    height = int(summary["height_px"])
    ratio = width / max(1, height)
    min_dimension = min(width, height)
    max_dimension = max(width, height)
    stem = path.stem
    role = _figure_role(stem, artifact_kind=artifact_kind, claim_tier=claim_tier)
    payload: VisualQualitySummary = {
        "width_px": width,
        "height_px": height,
        "aspect_ratio": round(ratio, 3),
        "aspect_class": _aspect_class(ratio, artifact_kind=artifact_kind, stem=stem),
        "label_density": _label_density(
            width,
            height,
            artifact_kind=artifact_kind,
            stem=stem,
        ),
        "manuscript_use": _manuscript_use(priority, manuscript_label),
        "min_dimension_px": min_dimension,
        "max_dimension_px": max_dimension,
        "figure_role": role,
        "readability_status": _readability_status(
            min_dimension,
            width,
            height,
            priority=priority,
            role=role,
        ),
    }
    split_group = _split_group(stem)
    if split_group:
        payload["split_group"] = split_group
    exception = _readability_exception(stem, role, payload["readability_status"])
    if exception:
        payload["readability_exception"] = exception
    return payload


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


def write_figure_artifacts(
    path: Path,
    plot_data: dict[str, Any],
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
    """Write raw plot data and metadata sidecar for one figure."""

    data_path = write_figure_plot_data(path, plot_data)
    return write_figure_sidecar(
        path,
        title=title,
        backend=backend,
        fidelity=fidelity,
        source_data=source_data,
        validation_status=validation_status,
        regeneration_command=regeneration_command,
        metrics=metrics,
        caption=caption,
        alt_text=alt_text,
        manuscript_section=manuscript_section,
        manuscript_label=manuscript_label,
        claim_tier=claim_tier,
        citation_keys=citation_keys,
        source_dois=source_dois,
        accessibility_checks=accessibility_checks,
        design_citation_keys=design_citation_keys,
        design_source_dois=design_source_dois,
        unsupported_inference=unsupported_inference,
        priority=priority,
        artifact_kind=artifact_kind,
        plot_data_path=project_relative_path(data_path),
    )


def write_figure_sidecar(
    path: Path,
    *,
    title: str,
    backend: str,
    fidelity: str,
    source_data: str,
    validation_status: str,
    regeneration_command: str,
    plot_data_path: str | None = None,
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
    effective_priority = priority or str(narrative_fields.get("priority", "indexed"))
    effective_label = manuscript_label or str(narrative_fields.get("manuscript_label", ""))
    effective_kind = artifact_kind or str(narrative_fields.get("artifact_kind", "figure"))
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
        "visual_quality": visual_quality_summary(
            path,
            quality=quality,
            priority=effective_priority,
            manuscript_label=effective_label,
            artifact_kind=effective_kind,
            claim_tier=str(narrative_fields.get("claim_tier", "")),
        ),
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
    if plot_data_path:
        payload["plot_data_path"] = plot_data_path
    sidecar = path.with_suffix(".json")
    sidecar.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return sidecar


def _aspect_class(ratio: float, *, artifact_kind: str, stem: str) -> str:
    if artifact_kind == "animation" or "contact_sheet" in stem:
        return "contact_sheet"
    if ratio < 0.72:
        return "tall"
    if ratio > 2.15:
        return "wide"
    return "balanced"


def _label_density(width: int, height: int, *, artifact_kind: str, stem: str) -> str:
    if artifact_kind == "animation" or "contact_sheet" in stem:
        return "frame_strip"
    dense_names = ("claim_map", "dashboard", "matrix", "network", "graph", "evidence_index")
    if any(name in stem for name in dense_names) or width * height >= 2_200_000:
        return "dense"
    if width * height >= 1_000_000:
        return "moderate"
    return "compact"


def _figure_role(stem: str, *, artifact_kind: str, claim_tier: str | None) -> str:
    if artifact_kind == "animation" or "contact_sheet" in stem:
        return "contact_sheet"
    if stem.endswith("_detail") or "detail" in stem:
        return "detail"
    lowered = f"{stem} {claim_tier or ''}".lower()
    if any(token in lowered for token in ("dashboard", "scorecard", "heatmap", "matrix")):
        return "dashboard"
    return "overview"


def _split_group(stem: str) -> str:
    groups = {
        "manuscript_figure_claim_map": "manuscript_figure_claims",
        "manuscript_figure_claim_detail": "manuscript_figure_claims",
        "methods_repo_dashboard": "methods_dashboard",
        "methods_dashboard_detail": "methods_dashboard",
        "research_fidelity_evidence_network": "research_evidence",
        "research_evidence_detail": "research_evidence",
        "stack_synthesis_dashboard": "stack_synthesis",
        "stack_synthesis_findings_detail": "stack_synthesis",
    }
    return groups.get(stem, "")


def _readability_status(
    min_dimension: int,
    width: int,
    height: int,
    *,
    priority: str | None,
    role: str,
) -> str:
    if priority != "primary":
        return "gallery"
    if role == "contact_sheet":
        return "pass" if width >= 1200 and height >= 520 else "exception"
    if role == "detail":
        return "pass" if min_dimension >= 780 else "exception"
    if role == "dashboard":
        return "pass" if min_dimension >= 840 else "exception"
    return "pass" if min_dimension >= 700 else "exception"


def _readability_exception(stem: str, role: str, status: str) -> str:
    if status != "exception":
        return ""
    if role == "contact_sheet":
        return (
            "contact sheet source raster is frame-strip evidence; preserve generated frame aspect"
        )
    if stem in {"connectome_completeness_tiers"}:
        return "compact tier summary intentionally uses fewer labels"
    return "registered dense manuscript figure has a split companion or constrained label set"


def _manuscript_use(priority: str | None, manuscript_label: str | None) -> str:
    if priority == "primary":
        return "manuscript_primary"
    if priority == "supporting":
        return "supporting_gallery"
    if priority == "indexed":
        return "indexed_gallery"
    if manuscript_label:
        return "manuscript_referenced"
    return "generated_gallery"
