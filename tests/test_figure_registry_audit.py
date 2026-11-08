from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

from beestack.figure_audit import audit_figures
from beestack.visualization.figure_registry import (
    figure_narrative_for_path,
)


def _varied_png(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(23)
    arr = (rng.random((32, 40, 3)) * 255).astype(np.uint8)
    Image.fromarray(arr, "RGB").save(path)
    return path


def test_all_inserted_manuscript_figures_have_curated_registry_narratives() -> None:
    project_root = Path(__file__).resolve().parents[1]
    image_re = re.compile(r"!\[[^\]]+\]\((?P<path>[^)]+)\)\{#fig:(?P<label>[^}\s]+)")
    references: list[tuple[str, str]] = []
    for markdown_path in sorted((project_root / "output" / "manuscript").glob("*.md")):
        for match in image_re.finditer(markdown_path.read_text(encoding="utf-8")):
            resolved = (markdown_path.parent / match.group("path")).resolve()
            artifact = resolved.relative_to(project_root.resolve()).as_posix()
            references.append((artifact, match.group("label")))

    assert references
    for artifact, label in references:
        narrative = figure_narrative_for_path(artifact)
        assert narrative is not None, artifact
        assert narrative.priority == "primary", artifact
        assert narrative.manuscript_label == f"fig:{label}"


def test_figure_audit_detects_path_label_sidecar_and_primary_failures(tmp_path: Path) -> None:
    manuscript = tmp_path / "output" / "manuscript"
    figures = tmp_path / "output" / "figures"
    manuscript.mkdir(parents=True)
    _varied_png(figures / "present.png")
    _varied_png(figures / "primary.png")
    (figures / "primary.json").write_text("{}", encoding="utf-8")
    (manuscript / "01.md").write_text(
        "\n".join(
            (
                "![Present figure](../figures/present.png){#fig:dup}",
                "![Missing figure](../figures/missing.png){#fig:dup}",
                "![Primary figure](../figures/primary.png){#fig:primary}",
                "![Absent evidence supports validation](../figures/primary.png){#fig:absent}",
            )
        ),
        encoding="utf-8",
    )

    audit = audit_figures(
        tmp_path,
        required_primary_artifacts=("output/figures/primary.png", "output/figures/absent.png"),
        absent_artifacts=("output/figures/primary.png",),
    )

    assert not audit.passed
    assert "output/manuscript/01.md:../figures/missing.png" in audit.missing_image_paths
    assert "dup" in audit.duplicate_labels
    assert "output/figures/present.json" in audit.missing_sidecar_paths
    assert audit.missing_high_priority_artifacts == ("output/figures/absent.png",)
    assert audit.absent_positive_claims


def test_figure_audit_detects_sidecar_mismatch_and_absolute_path_leakage(
    tmp_path: Path,
) -> None:
    manuscript = tmp_path / "output" / "manuscript"
    figures = tmp_path / "output" / "figures"
    manuscript.mkdir(parents=True)
    figure_path = _varied_png(figures / "registered.png")
    (figures / "registered.json").write_text(
        json.dumps(
            {
                "figure_path": str(figure_path),
                "title": "Registered",
                "backend": "Matplotlib",
                "fidelity": "diagnostic",
                "source_data": "test fixture",
                "validation_status": "nonblank",
                "regeneration_command": "uv run python scripts/analysis_pipeline.py",
                "caption": "Different caption.",
                "alt_text": "Alt text.",
                "manuscript_section": "manuscript/01.md",
                "manuscript_label": "fig:sidecar-label",
                "claim_tier": "diagnostic",
                "unsupported_inference": "Does not support external claims.",
                "artifact_kind": "figure",
            }
        ),
        encoding="utf-8",
    )
    (manuscript / "01.md").write_text(
        "![Manuscript caption](../figures/registered.png){#fig:markdown-label}\n",
        encoding="utf-8",
    )

    audit = audit_figures(
        tmp_path,
        required_primary_artifacts=("output/figures/registered.png",),
    )

    assert not audit.passed
    assert "output/figures/registered.json:figure_path" in audit.absolute_path_leaks
    assert "output/figures/registered.json:manuscript_label" in audit.sidecar_manuscript_mismatches
    assert "output/figures/registered.json:caption" in audit.sidecar_manuscript_mismatches


def test_figure_audit_detects_missing_sidecar_narrative_fields(tmp_path: Path) -> None:
    manuscript = tmp_path / "output" / "manuscript"
    figures = tmp_path / "output" / "figures"
    manuscript.mkdir(parents=True)
    _varied_png(figures / "incomplete.png")
    (figures / "incomplete.json").write_text(
        json.dumps(
            {
                "figure_path": "output/figures/incomplete.png",
                "title": "Incomplete",
                "backend": "Matplotlib",
            }
        ),
        encoding="utf-8",
    )
    (manuscript / "01.md").write_text(
        "![Incomplete](../figures/incomplete.png){#fig:incomplete}\n",
        encoding="utf-8",
    )

    audit = audit_figures(
        tmp_path,
        required_primary_artifacts=("output/figures/incomplete.png",),
    )

    assert not audit.passed
    assert "output/figures/incomplete.json:caption" in audit.sidecar_required_field_failures
    assert "output/figures/incomplete.json:artifact_kind" in audit.sidecar_required_field_failures


def test_figure_audit_allows_plot_data_without_narrative_fields(tmp_path: Path) -> None:
    manuscript = tmp_path / "output" / "manuscript"
    figures = tmp_path / "output" / "figures"
    manuscript.mkdir(parents=True)
    figure_path = _varied_png(figures / "plotdata.png")
    (figures / "plotdata.json").write_text(
        json.dumps(
            {
                "schema": "beestack.figure.v1",
                "figure_path": "output/figures/plotdata.png",
                "title": "Plot Data Figure",
                "backend": "Matplotlib",
                "fidelity": "diagnostic",
                "source_data": "output/data/run_summary.json",
                "validation_status": "nonblank",
                "regeneration_command": "uv run python scripts/analysis_pipeline.py",
                "caption": (
                    "Matplotlib plot data figure generated from output data; "
                    "sidecar-validated raster. Does not support external claims."
                ),
                "alt_text": "Plot data figure.",
                "manuscript_section": "manuscript/01.md",
                "manuscript_label": "fig:plotdata",
                "claim_tier": "diagnostic",
                "unsupported_inference": "Does not support external claims.",
                "artifact_kind": "figure",
            }
        ),
        encoding="utf-8",
    )
    (figures / "plotdata_data.json").write_text(
        json.dumps({"schema": "beestack.figure_data.v1", "figure_path": str(figure_path)}),
        encoding="utf-8",
    )
    (manuscript / "01.md").write_text(
        (
            "![Matplotlib plot data figure generated from output data; "
            "sidecar-validated raster. Does not support external claims.]"
            "(../figures/plotdata.png){#fig:plotdata}\n"
        ),
        encoding="utf-8",
    )

    audit = audit_figures(
        tmp_path,
        required_primary_artifacts=("output/figures/plotdata.png",),
    )

    assert not any("plotdata_data.json" in item for item in audit.sidecar_required_field_failures)
    assert "output/figures/plotdata_data.json:figure_path" in audit.absolute_path_leaks


def test_figure_audit_detects_primary_caption_contract_failures(tmp_path: Path) -> None:
    manuscript = tmp_path / "output" / "manuscript"
    figures = tmp_path / "output" / "figures"
    manuscript.mkdir(parents=True)
    _varied_png(figures / "primary.png")
    (figures / "primary.json").write_text(
        json.dumps(
            {
                "figure_path": "output/figures/primary.png",
                "title": "Primary",
                "backend": "Matplotlib",
                "fidelity": "diagnostic",
                "source_data": "output/data/run_summary.json",
                "validation_status": "nonblank",
                "regeneration_command": "uv run python scripts/analysis_pipeline.py",
                "caption": "Primary generated figure.",
                "alt_text": "Primary figure.",
                "manuscript_section": "manuscript/01.md",
                "manuscript_label": "fig:primary",
                "claim_tier": "diagnostic",
                "unsupported_inference": "Does not support external claims.",
                "artifact_kind": "figure",
                "priority": "primary",
            }
        ),
        encoding="utf-8",
    )
    (manuscript / "01.md").write_text(
        "![Primary generated figure.](../figures/primary.png){#fig:primary}\n",
        encoding="utf-8",
    )

    audit = audit_figures(
        tmp_path,
        required_primary_artifacts=("output/figures/primary.png",),
    )

    assert not audit.passed
    assert "output/figures/primary.json:caption_contract" in (
        audit.primary_caption_contract_failures
    )


def test_figure_audit_accepts_compound_backend_caption_contract(tmp_path: Path) -> None:
    manuscript = tmp_path / "output" / "manuscript"
    figures = tmp_path / "output" / "figures"
    manuscript.mkdir(parents=True)
    _varied_png(figures / "primary.png")
    (figures / "primary.json").write_text(
        json.dumps(
            {
                "figure_path": "output/figures/primary.png",
                "title": "Primary",
                "backend": "Matplotlib empirical-data renderer",
                "fidelity": "diagnostic",
                "source_data": "output/data/run_summary.json",
                "validation_status": "nonblank",
                "regeneration_command": "uv run python scripts/analysis_pipeline.py",
                "caption": "Empirical diagnostic.",
                "alt_text": "Primary figure.",
                "manuscript_section": "manuscript/01.md",
                "manuscript_label": "fig:primary",
                "claim_tier": "diagnostic",
                "unsupported_inference": "Does not support external claims.",
                "artifact_kind": "figure",
                "priority": "primary",
            }
        ),
        encoding="utf-8",
    )
    (manuscript / "01.md").write_text(
        (
            "![Matplotlib empirical diagnostic generated from output data; "
            "sidecar validation checks the raster, and the figure supports "
            "availability review rather than external validation.]"
            "(../figures/primary.png){#fig:primary}\n"
        ),
        encoding="utf-8",
    )

    audit = audit_figures(
        tmp_path,
        required_primary_artifacts=("output/figures/primary.png",),
    )

    assert not audit.primary_caption_contract_failures
