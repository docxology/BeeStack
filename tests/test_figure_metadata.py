"""Real-image coverage for visualization.figure_metadata (no mocks, real PIL)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from beestack.visualization.figure_metadata import (
    assert_nonblank_quality,
    image_quality_summary,
    write_figure_artifacts,
    write_figure_sidecar,
)
from beestack.visualization.figure_plot_data import figure_data_path
from beestack.visualization.style import contrast_ratio, wcag_contrast_check
from beestack.visualization.visual_quality import visual_quality_payload


def _varied_png(path: Path) -> Path:
    rng = np.random.default_rng(7)
    arr = (rng.random((24, 32, 3)) * 255).astype(np.uint8)
    Image.fromarray(arr, "RGB").save(path)
    return path


def _blank_png(path: Path) -> Path:
    Image.fromarray(np.zeros((16, 16, 3), dtype=np.uint8), "RGB").save(path)
    return path


def test_image_quality_summary_real_image(tmp_path: Path) -> None:
    summary = image_quality_summary(_varied_png(tmp_path / "v.png"))
    assert summary["width_px"] == 32
    assert summary["height_px"] == 24
    assert summary["mode"] == "RGB"  # reports the source image mode
    assert summary["nonzero_histogram_bins"] >= 8
    assert float(summary["std_intensity"]) > 0.0
    assert 0 <= int(summary["min_intensity"]) <= int(summary["max_intensity"]) <= 255


def test_assert_nonblank_quality_pass_and_fail(tmp_path: Path) -> None:
    ok = assert_nonblank_quality(_varied_png(tmp_path / "v.png"))
    assert float(ok["std_intensity"]) > 0.0
    with pytest.raises(ValueError, match="near-uniform|blank"):
        assert_nonblank_quality(_blank_png(tmp_path / "b.png"))


def test_write_figure_artifacts_writes_plot_data_and_sidecar(tmp_path: Path) -> None:
    fig = _varied_png(tmp_path / "fig.png")
    sidecar = write_figure_artifacts(
        fig,
        {
            "chart_type": "timeseries",
            "title": "Energy",
            "x_key": "step_index",
            "x": [0, 1],
            "series": {"energy_j": [1.0, 0.9]},
        },
        title="BeeBody energy",
        backend="matplotlib",
        fidelity="reduced",
        source_data="output/data/run_summary.json",
        validation_status="nonblank",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
    )
    data_path = figure_data_path(fig)
    assert data_path.exists()
    data_payload = json.loads(data_path.read_text(encoding="utf-8"))
    assert data_payload["schema"] == "beestack.figure_data.v1"
    assert data_payload["series"]["energy_j"] == [1.0, 0.9]
    payload = json.loads(sidecar.read_text(encoding="utf-8"))
    assert payload["plot_data_path"]
    assert payload["visual_quality"]["manuscript_use"] == "indexed_gallery"
    assert payload["visual_quality"]["aspect_class"] == "balanced"
    assert payload["visual_quality"]["figure_role"] == "overview"
    assert payload["visual_quality"]["readability_status"] == "gallery"


def test_write_figure_artifacts_normalizes_project_local_plot_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    fig = _varied_png(tmp_path / "fig.png")
    sidecar = write_figure_artifacts(
        fig,
        {
            "chart_type": "contact_sheet",
            "title": "Contact sheet",
            "source_gif": str(tmp_path / "source.gif"),
            "frame_count": 8,
        },
        title="Contact sheet",
        backend="matplotlib",
        fidelity="contact sheet",
        source_data="output/data/run_summary.json",
        validation_status="nonblank",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
    )
    data_payload = json.loads(figure_data_path(fig).read_text(encoding="utf-8"))

    assert data_payload["source_gif"] == "source.gif"
    assert data_payload["figure_path"] == "fig.png"
    assert json.loads(sidecar.read_text(encoding="utf-8"))["plot_data_path"] == "fig_data.json"


def test_write_figure_sidecar(tmp_path: Path) -> None:
    fig = _varied_png(tmp_path / "fig.png")
    sidecar = write_figure_sidecar(
        fig,
        title="BeeBody energy",
        backend="matplotlib",
        fidelity="reduced",
        source_data="output/data/run_summary.json",
        validation_status="nonblank",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        metrics={"final_energy_j": 0.42},
    )
    assert sidecar == fig.with_suffix(".json")
    assert sidecar.exists()
    payload = json.loads(sidecar.read_text(encoding="utf-8"))
    assert payload["schema"] == "beestack.figure.v1"
    assert payload["title"] == "BeeBody energy"
    assert payload["backend"] == "matplotlib"
    assert payload["fidelity"] == "reduced"
    assert payload["metrics"]["final_energy_j"] == 0.42
    assert payload["quality"]["width_px"] == 32
    assert payload["visual_quality"]["width_px"] == 32
    assert payload["visual_quality"]["height_px"] == 24
    assert payload["visual_quality"]["label_density"] == "compact"
    assert payload["visual_quality"]["figure_role"] == "overview"
    assert payload["visual_quality"]["readability_status"] == "gallery"


def test_write_figure_sidecar_accepts_explicit_narrative_metadata(tmp_path: Path) -> None:
    fig = _varied_png(tmp_path / "custom.png")
    sidecar = write_figure_sidecar(
        fig,
        title="Custom",
        backend="matplotlib",
        fidelity="reduced",
        source_data="output/data/custom.json",
        validation_status="nonblank",
        regeneration_command="uv run python scripts/custom.py",
        caption="Custom caption for manuscript placement.",
        alt_text="Custom alt text.",
        manuscript_section="manuscript/99_references.md",
        manuscript_label="fig:custom",
        claim_tier="diagnostic",
        citation_keys=("wilson2017good",),
        source_dois=("10.1371/journal.pcbi.1005510",),
        accessibility_checks={"normal_text_passed": True, "contrast_ratio": 12.0},
        design_citation_keys=("rougier2014figures",),
        design_source_dois=("10.1371/journal.pcbi.1003833",),
        unsupported_inference="Does not support biological validation.",
        priority="secondary",
    )

    payload = json.loads(sidecar.read_text(encoding="utf-8"))
    assert payload["caption"] == "Custom caption for manuscript placement."
    assert payload["alt_text"] == "Custom alt text."
    assert payload["manuscript_section"] == "manuscript/99_references.md"
    assert payload["manuscript_label"] == "fig:custom"
    assert payload["citation_keys"] == ["wilson2017good"]
    assert payload["source_dois"] == ["10.1371/journal.pcbi.1005510"]
    assert payload["accessibility_checks"]["normal_text_passed"] is True
    assert payload["design_citation_keys"] == ["rougier2014figures"]
    assert payload["design_source_dois"] == ["10.1371/journal.pcbi.1003833"]
    assert payload["unsupported_inference"] == "Does not support biological validation."
    assert payload["visual_quality"]["manuscript_use"] == "manuscript_referenced"
    assert payload["visual_quality"]["readability_status"] == "gallery"


def test_write_figure_sidecar_without_metrics(tmp_path: Path) -> None:
    fig = _varied_png(tmp_path / "g.png")
    sidecar = write_figure_sidecar(
        fig,
        title="t",
        backend="b",
        fidelity="f",
        source_data="s",
        validation_status="v",
        regeneration_command="r",
    )
    payload = json.loads(sidecar.read_text(encoding="utf-8"))
    assert "metrics" not in payload
    assert payload["accessibility_checks"]["normal_text_passed"]


def test_wcag_contrast_helpers_are_deterministic() -> None:
    assert contrast_ratio("#111827", "#ffffff") >= 12.0
    good = wcag_contrast_check("#111827", "#ffffff")
    poor = wcag_contrast_check("#777777", "#888888")

    assert good["normal_text_passed"] is True
    assert good["large_text_passed"] is True
    assert poor["normal_text_passed"] is False
    assert poor["standard"] == "WCAG 2.1 AA contrast thresholds"


def test_visual_quality_report_requires_primary_role_and_readability(tmp_path: Path) -> None:
    (tmp_path / "output" / "figures").mkdir(parents=True)
    figure = _varied_png(tmp_path / "output" / "figures" / "beestack_graphical_abstract.png")
    write_figure_sidecar(
        figure,
        title="BeeStack graphical abstract",
        backend="Matplotlib",
        fidelity="architecture schematic",
        source_data="output/data/run_summary.json",
        validation_status="nonblank",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
    )

    payload = visual_quality_payload(tmp_path)
    graphical = next(
        item
        for item in payload["items"]
        if item["artifact_path"] == "output/figures/beestack_graphical_abstract.png"
    )

    assert graphical["figure_role"] == "overview"
    assert graphical["readability_status"] in {"pass", "exception"}
    assert payload["primary_figure_count"] >= 1
    assert any("missing metadata sidecar" in blocker for blocker in payload["blockers"])
