"""Real parser-to-figure boundaries for schematic, partial, and supported pathways."""

from __future__ import annotations

import json
import math
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from matplotlib.patches import FancyArrowPatch

from beestack.brain.anatomy import AtlasInventory, atlas_inventory_from_zip
from beestack.brain.connectome import (
    BeeBrainConnectomeReport,
    build_structural_connectome,
    connectome_tiers_from_report,
)
from beestack.brain.datasets import honeybee_standard_brain_assets
from beestack.visualization.connectome_figures import (
    _structural_graph_figure,
    generate_connectome_figures,
)
from beestack.visualization.figure_plot_data import figure_data_path
from beestack.visualization.figure_plot_specs import (
    connectome_graph,
    connectome_plot_data,
    empirical_plot_data,
)

PATHWAY_ASSETS = ("hsb-vrml-alf1", "hsb-vrml-act", "hsb-vrml-pe1-pn")


def _local_report(
    root: Path, asset_ids: tuple[str, ...]
) -> tuple[BeeBrainConnectomeReport, tuple[AtlasInventory, ...]]:
    """Write tiny valid VRML parser inputs, not claimed biological anatomy."""

    atlas = root / "virtual-honeybee-standard-brain"
    atlas.mkdir(parents=True)
    inventories = []
    for index, asset in enumerate(honeybee_standard_brain_assets()):
        if asset.asset_id not in asset_ids:
            continue
        x = index * 10
        vrml = (
            "#VRML V2.0 utf8\n"
            f"DEF FixtureProjection{index} Transform {{ children [ Shape {{ "
            "geometry IndexedFaceSet { coord Coordinate { point [ "
            f"{x} 0 0, {x + 3} 0 0, {x} 3 0 "
            "] } coordIndex [ 0, 1, 2, -1 ] } } ] }"
        )
        archive_path = atlas / asset.file_name
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("fixture.wrl", vrml)
        inventory = atlas_inventory_from_zip(archive_path, asset_id=asset.asset_id)
        assert inventory.vrml_vertex_count == 3
        assert inventory.vrml_centroid is not None
        inventories.append(inventory)
    parsed = tuple(inventories)
    return build_structural_connectome(root, inventories=parsed), parsed


def _projection(
    report: BeeBrainConnectomeReport, inventories: tuple[AtlasInventory, ...]
) -> dict[str, object]:
    return empirical_plot_data(
        Path("empirical_anatomy_projection.png"),
        panels=(),
        panel_stats=(),
        stack_alignment={},
        anatomy_inventories=inventories,
        connectome_report=report,
    )


@pytest.mark.parametrize("supported_count", [0, 1, 3])
def test_real_graph_render_and_sidecar_preserve_fidelity(
    tmp_path: Path, supported_count: int
) -> None:
    report, _inventories = _local_report(tmp_path / "sources", PATHWAY_ASSETS[:supported_count])
    expected_state = {
        0: "schematic_only",
        1: "mixed_structural_and_schematic",
        3: "structural_projectome",
    }[supported_count]
    expected_claim = "structural_projectome_witness" if supported_count == 3 else expected_state
    expected_counts = {
        "structural_tract": supported_count * 2,
        "schematic_pathway": (3 - supported_count) * 2,
    }
    assert report.tier == ("schematic_only" if supported_count == 0 else "structural_projectome")
    assert report.completeness["structural_coverage"] == pytest.approx(supported_count / 3)
    graph = connectome_graph(report)
    assert graph.number_of_edges() == len(report.edges) == 6
    for kind, expected in expected_counts.items():
        assert sum(data["edge_kind"] == kind for *_, data in graph.edges(data=True)) == expected

    figure = _structural_graph_figure(report)
    try:
        axes = figure.axes[0]
        arrows = [patch for patch in axes.patches if isinstance(patch, FancyArrowPatch)]
        assert len(arrows) == 3
        assert sum(arrow.get_linestyle() == "--" for arrow in arrows) == 3 - supported_count
        assert sum(arrow.get_linestyle() == "-" for arrow in arrows) == supported_count
        title = axes.get_title(loc="left").lower()
        if supported_count == 0:
            assert "schematic" in title
            assert "structural projectome" not in title
        elif supported_count == 1:
            assert "mixed" in title and "schematic" in title
        else:
            assert "structural projectome" in title
    finally:
        plt.close(figure)

    # A stale aggregate cannot replace the graph's actual structural coverage.
    tiers = connectome_tiers_from_report(report)
    tiers["structural"]["coverage"] = 1.0
    paths = generate_connectome_figures(
        report,
        tmp_path / "output" / "figures" / "empirical",
        completeness_tiers=tiers,
        project_root=tmp_path,
    )
    assert len(paths) == 3
    for path in paths:
        sidecar = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        plot = json.loads(figure_data_path(path).read_text(encoding="utf-8"))
        assert sidecar["claim_tier"] == expected_claim
        assert sidecar["fidelity"] == plot["fidelity"]
        assert sidecar["metrics"]["tier"] == plot["tier"] == report.tier
        assert sidecar["metrics"]["evidence_state"] == plot["evidence_state"] == expected_state
        assert sidecar["metrics"]["edge_counts"] == plot["edge_counts"] == expected_counts
        assert sidecar["metrics"]["supporting_assets"] == list(report.supporting_assets)
        assert expected_state in sidecar["caption"]
        assert expected_state in sidecar["alt_text"]
        assert expected_state in sidecar["validation_status"]
        assert sidecar["quality"]["std_intensity"] > 0
        assert sidecar["source_data"] == "output/data/bee_brain_connectome.json"
        assert sidecar["plot_data_path"].startswith("output/")
        if path.stem == "connectome_structural_graph":
            expected_edges = {
                (edge.source_id, edge.target_id, edge.edge_kind, edge.evidence)
                for edge in report.edges
            }
            assert {
                (edge["source"], edge["target"], edge["edge_kind"], edge["evidence"])
                for edge in plot["edges"]
            } == expected_edges
            assert len(plot["edges"]) == 6
            for edge in plot["edges"]:
                assert edge["kind"] == edge["edge_kind"]
                assert edge["line_style"] == (
                    "dashed" if edge["edge_kind"] == "schematic_pathway" else "solid"
                )
            assert all(math.isfinite(node[axis]) for node in plot["nodes"] for axis in ("x", "y"))
        elif path.stem == "connectome_completeness_tiers":
            coverage = {row["tier"]: row["coverage"] for row in plot["rows"]}
            assert coverage["structural"] == pytest.approx(supported_count / 3)
            assert coverage["functional"] == coverage["synaptic"] == 0.0


@pytest.mark.parametrize("supported_count", [0, 1, 3])
def test_spatial_export_never_gives_schematic_edges_coordinates(
    tmp_path: Path, supported_count: int
) -> None:
    report, inventories = _local_report(tmp_path, PATHWAY_ASSETS[:supported_count])
    plot = _projection(report, inventories)
    assert plot["geometry_node_count"] == len(inventories)
    assert plot["geometry_available"] is bool(inventories)
    assert plot["schematic_edge_count_excluded"] == (3 - supported_count) * 2
    assert plot["geometry_edge_count"] == len(plot["edges"])
    assert plot["structural_overlay_available"] is bool(plot["edges"])
    source_edges = {
        (edge.source_id, edge.target_id, edge.edge_kind, edge.evidence)
        for edge in report.edges
        if edge.edge_kind == "structural_tract"
    }
    for edge in plot["edges"]:
        assert (edge["source"], edge["target"], edge["edge_kind"], edge["evidence"]) in source_edges
        assert edge["kind"] == "structural_tract"
        for axis, keys in ((0, ("x0", "x1")), (1, ("y0", "y1"))):
            coordinates = [inventory.vrml_centroid[axis] for inventory in inventories]
            assert all(min(coordinates) <= edge[key] <= max(coordinates) for key in keys)
    if supported_count:
        assert plot["edges"]
        assert plot["claim_tier"] == "structural_projectome_witness"
    else:
        assert plot["nodes"] == plot["edges"] == []
        assert "unavailable" in plot["fidelity"]
        assert plot["claim_tier"] == "empirical_availability_diagnostic"


def test_unrelated_geometry_does_not_support_schematic_tracts(tmp_path: Path) -> None:
    report, inventories = _local_report(tmp_path, ("hsb-vrml-atlas",))
    assert report.supporting_assets == ("hsb-vrml-atlas",)
    assert report.tier == "schematic_only"
    semantic = connectome_plot_data(Path("connectome_structural_graph.png"), report=report)
    assert len(semantic["edges"]) == 6
    assert semantic["claim_tier"] == "schematic_only"
    assert semantic["edge_counts"] == {"structural_tract": 0, "schematic_pathway": 6}
    spatial = _projection(report, inventories)
    assert len(spatial["nodes"]) == 1
    assert spatial["edges"] == []
    assert spatial["geometry_available"] is True
    assert spatial["structural_overlay_available"] is False
    assert spatial["claim_tier"] == "empirical_availability_diagnostic"
    assert "centroid projection only" in spatial["fidelity"]


def test_runtime_spatial_sidecar_does_not_promote_centroids_to_tract_evidence(
    odor_fixture_project,
) -> None:
    from beestack.brain.empirical_pipeline import build_empirical_analysis_bundle
    from beestack.visualization.empirical_figures import generate_empirical_figures

    root, cfg = odor_fixture_project
    report, inventories = _local_report(root / "output/data/empirical_sources", ("hsb-vrml-atlas",))
    bundle = build_empirical_analysis_bundle(cfg, root)
    assert bundle is not None
    output = root / "output/figures/empirical"
    generate_empirical_figures(
        bundle.panels,
        bundle.stats,
        bundle.alignment,
        output,
        anatomy_summary=bundle.anatomy_summary,
        anatomy_inventories=inventories,
        connectome_report=report,
        project_root=root,
    )
    sidecar = json.loads((output / "empirical_anatomy_projection.json").read_text())
    assert sidecar["claim_tier"] == "empirical_availability_diagnostic"
    assert sidecar["metrics"]["geometry_available"] is True
    assert sidecar["metrics"]["structural_overlay_available"] is False
    assert sidecar["metrics"]["geometry_edge_count"] == 0
    assert sidecar["metrics"]["schematic_edge_count_excluded"] == 6
