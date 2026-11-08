"""Tests for BeeBrain structural connectome graph assembly."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from beestack.brain.connectome import build_structural_connectome, connectome_tiers_from_report
from beestack.brain.datasets import honeybee_standard_brain_assets


@pytest.fixture(scope="module")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def source_dir(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("structural-assets")
    atlas = root / "virtual-honeybee-standard-brain"
    atlas.mkdir()
    for asset in honeybee_standard_brain_assets():
        if asset.asset_id in {"hsb-vrml-alf1", "hsb-vrml-act", "hsb-vrml-pe1-pn"}:
            with zipfile.ZipFile(atlas / asset.file_name, "w") as archive:
                archive.writestr("neuron.wrl", "#VRML V2.0 utf8\nDEF ProjectionNeuron Transform {}")
    return root


def test_structural_connectome_from_local_hsb_assets(source_dir: Path) -> None:
    report = build_structural_connectome(source_dir)
    assert report.tier == "structural_projectome"
    assert report.nodes
    structural_edges = [edge for edge in report.edges if edge.edge_kind == "structural_tract"]
    assert structural_edges
    assert all(edge.edge_kind != "synaptic" for edge in report.edges)
    assert all(node.provenance_doi for node in report.nodes)
    tiers = connectome_tiers_from_report(report)
    assert tiers["structural"]["available"] is True
    assert tiers["synaptic"]["tier"] == "synaptic_unavailable"
    assert tiers["synaptic"]["edge_count"] == 0
    assert tiers["functional"]["edge_count"] == 0
    assert "VAR_connectivity" in str(tiers["functional"]["blocker"])


def test_connectome_json_roundtrip_fields(source_dir: Path, tmp_path: Path) -> None:
    report = build_structural_connectome(source_dir)
    payload = report.as_dict()
    out = tmp_path / "bee_brain_connectome.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["tier"] == "structural_projectome"
    assert loaded["edge_count"] >= 1
    assert loaded["completeness"]["synaptic_coverage"] == 0.0


def test_missing_assets_leave_only_schematic_pathways(tmp_path: Path) -> None:
    report = build_structural_connectome(tmp_path)
    assert report.tier == "schematic_only"
    assert report.edges
    assert {edge.edge_kind for edge in report.edges} == {"schematic_pathway"}
    assert report.completeness["structural_coverage"] == 0.0
    assert report.supporting_assets == ()
    assert connectome_tiers_from_report(report)["structural"]["available"] is False


def test_one_supporting_asset_has_one_third_coverage(tmp_path: Path) -> None:
    atlas = tmp_path / "virtual-honeybee-standard-brain"
    atlas.mkdir()
    asset = next(
        asset for asset in honeybee_standard_brain_assets() if asset.asset_id == "hsb-vrml-alf1"
    )
    with zipfile.ZipFile(atlas / asset.file_name, "w") as archive:
        archive.writestr("one.wrl", "DEF ALF1 Transform {}")
    report = build_structural_connectome(tmp_path)
    assert report.supporting_assets == ("hsb-vrml-alf1",)
    assert report.completeness["structural_coverage"] == pytest.approx(1 / 3)
    assert sum(edge.edge_kind == "structural_tract" for edge in report.edges) == 2
