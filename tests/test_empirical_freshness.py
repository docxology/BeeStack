"""Skipped/failed acquisition must never revive retained reports as current evidence."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from beestack.brain.empirical_status import (
    current_empirical_analysis,
    empirical_configuration_sha256,
    empirical_implementation_sha256,
    empirical_inputs_sha256,
)
from beestack.config import BeeStackConfig
from beestack.pipeline import run_empirical_analysis


def _seal(root: Path, report: Path) -> None:
    (report.parent / "empirical_availability.json").write_text(
        json.dumps(
            {
                "scope": "odor_response_panel_analysis",
                "current": True,
                "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
                "input_sha256": empirical_inputs_sha256(root),
                "implementation_sha256": empirical_implementation_sha256(),
                "configuration_sha256": empirical_configuration_sha256(BeeStackConfig()),
            }
        ),
        encoding="utf-8",
    )


def _retained(root: Path, *, sealed: bool) -> Path:
    data = root / "output/data"
    data.mkdir(parents=True)
    raw = data / "empirical_sources/fixture/files/input.csv"
    raw.parent.mkdir(parents=True)
    raw.write_text("odor,bee,response\nA,g1,1\n", encoding="utf-8")
    report = data / "empirical_analysis.json"
    report.write_text(json.dumps({"panel_count": 1}), encoding="utf-8")
    if sealed:
        _seal(root, report)
    return report


def test_skipped_stage_preserves_history_without_reusing_its_measurements(tmp_path: Path) -> None:
    report = _retained(tmp_path, sealed=True)
    prior = report.read_bytes()
    assert (
        current_empirical_analysis(tmp_path, BeeStackConfig())["availability_status"] == "current"
    )
    (tmp_path / "output/data/empirical_sources/fixture/files/input.csv").unlink()
    assert run_empirical_analysis(BeeStackConfig(), tmp_path) is False
    assert report.read_bytes() == prior
    current = current_empirical_analysis(tmp_path, BeeStackConfig())
    assert current["availability_status"] == "historical_unavailable"
    assert "panel_count" not in current


def test_unsealed_history_and_mutated_reports_are_not_current(tmp_path: Path) -> None:
    report = _retained(tmp_path, sealed=False)
    assert (
        current_empirical_analysis(tmp_path, BeeStackConfig())["availability_status"]
        == "historical_unavailable"
    )
    _seal(tmp_path, report)
    report.write_text(json.dumps({"panel_count": 99}), encoding="utf-8")
    assert (
        current_empirical_analysis(tmp_path, BeeStackConfig())["availability_status"]
        == "historical_unavailable"
    )


@pytest.mark.parametrize(
    "bad_marker", ["{", "[]", '{"current": "true"}', '{"scope": "other", "current": true}']
)
def test_malformed_or_wrong_scope_receipts_never_certify_history(
    tmp_path: Path, bad_marker: str
) -> None:
    report = _retained(tmp_path, sealed=True)
    (report.parent / "empirical_availability.json").write_text(bad_marker, encoding="utf-8")
    current = current_empirical_analysis(tmp_path, BeeStackConfig())
    assert current["availability_status"] == "historical_unavailable"
    assert "panel_count" not in current


@pytest.mark.parametrize("raw", [b"{", b"[]"])
def test_even_hash_matching_malformed_reports_are_unavailable(tmp_path: Path, raw: bytes) -> None:
    report = _retained(tmp_path, sealed=True)
    report.write_bytes(raw)
    _seal(tmp_path, report)
    assert (
        current_empirical_analysis(tmp_path, BeeStackConfig())["availability_status"]
        == "historical_unavailable"
    )


def test_successful_partial_refresh_demotes_ungenerated_optional_figures(
    odor_fixture_project,
) -> None:
    root, cfg = odor_fixture_project
    figures = root / "output/figures/empirical"
    figures.mkdir(parents=True)
    retained = figures / "waggle_follower_alignment.png"
    pixels = np.arange(12 * 12 * 3, dtype=np.uint8).reshape(12, 12, 3)
    Image.fromarray(pixels).save(retained)
    prior = retained.read_bytes()
    sidecar = retained.with_suffix(".json")
    sidecar.write_text(json.dumps({"availability_status": "current"}), encoding="utf-8")
    assert run_empirical_analysis(cfg, root) is True
    assert current_empirical_analysis(root, cfg)["availability_status"] == "current"
    assert retained.read_bytes() == prior
    assert json.loads(sidecar.read_text())["availability_status"] == "historical_unavailable"
    current_sidecar = figures / "empirical_panel_heatmap.json"
    assert json.loads(current_sidecar.read_text())["availability_status"] == "current"


@pytest.mark.parametrize("mutation", ["replace", "delete", "add"])
def test_changed_generating_input_set_cannot_retain_current_measurements(
    odor_fixture_project, mutation
):
    root, cfg = odor_fixture_project
    assert run_empirical_analysis(cfg, root)
    report = root / "output/data/empirical_analysis.json"
    original = report.read_bytes()
    assert current_empirical_analysis(root, cfg)["availability_status"] == "current"
    raw = next((root / "output/data/empirical_sources").rglob("*.xlsx"))
    if mutation == "delete":
        raw.unlink()
    elif mutation == "replace":
        from openpyxl import load_workbook

        book = load_workbook(raw)
        book.active["B2"] = 42
        book.save(raw)
        book.close()
    else:
        raw.with_name("additional.csv").write_text("odor,bee,response\nC,g1,5\n", encoding="utf-8")
    current = current_empirical_analysis(root, cfg)
    assert current["availability_status"] == "historical_unavailable"
    assert "panel_count" not in current
    assert report.read_bytes() == original


def test_changed_parameterization_cannot_reuse_a_prior_analysis(odor_fixture_project):
    root, cfg = odor_fixture_project
    assert run_empirical_analysis(cfg, root)
    assert current_empirical_analysis(root, cfg)["availability_status"] == "current"
    assert (
        current_empirical_analysis(root, replace(cfg, seed=cfg.seed + 1))["availability_status"]
        == "historical_unavailable"
    )


def test_unbound_implementation_receipt_cannot_certify_current_inputs(tmp_path):
    report = _retained(tmp_path, sealed=True)
    marker = report.parent / "empirical_availability.json"
    payload = json.loads(marker.read_text())
    payload.pop("implementation_sha256")
    marker.write_text(json.dumps(payload), encoding="utf-8")
    assert (
        current_empirical_analysis(tmp_path, BeeStackConfig())["availability_status"]
        == "historical_unavailable"
    )
