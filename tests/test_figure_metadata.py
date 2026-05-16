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
    write_figure_sidecar,
)


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
