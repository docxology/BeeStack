"""Tests for BeeBrain structural connectome graph assembly."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from beestack.brain.connectome import build_structural_connectome, connectome_tiers_from_report


@pytest.fixture(scope="module")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def source_dir(project_root: Path) -> Path:
    path = project_root / "output" / "data" / "empirical_sources"
    if not path.exists():
        pytest.skip("empirical_sources directory not present locally")
    return path


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
