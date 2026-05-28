"""Build structural connectome graphs from Honeybee Standard Brain VRML assets."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

from ...security import assert_safe_zip_member, validate_zip_archive_bounds
from ..anatomy import AtlasInventory, NeuropilAbbreviation
from ..datasets import honeybee_standard_brain_assets
from .graph import (
    BeeBrainConnectomeReport,
    ConnectomeEdge,
    ConnectomeNode,
    ConnectomeTier,
)

HSB_DOI = "10.1002/cne.20644"

STRUCTURAL_PATHWAYS: tuple[tuple[str, str, str, str], ...] = (
    (
        "tract:alf1-al-mb",
        "neuropil:antennal_lobe",
        "neuropil:mushroom_body",
        "ALF1 projection neuron geometry (Honeybee Standard Brain ALF1_Standard.zip)",
    ),
    (
        "tract:act-antennocerebralis",
        "neuropil:antennal_lobe",
        "neuropil:central_complex",
        "Antennocerebralis tract bundle (Honeybee Standard Brain ACT_Standard.zip)",
    ),
    (
        "tract:pe1-pn-mb-intrinsic",
        "neuropil:mushroom_body",
        "neuropil:central_complex",
        "Pe1/Pn mushroom-body intrinsic and projection context (Atlas_Pe1_PNII.zip)",
    ),
)

ASSET_MODULE_HINTS: dict[str, str] = {
    "hsb-vrml-alf1": "mushroom_body",
    "hsb-vrml-act": "antennal_lobe",
    "hsb-vrml-pe1-pn": "mushroom_body",
    "hsb-vrml-atlas": "whole_brain",
}


def build_structural_connectome(
    source_dir: Path,
    *,
    inventories: tuple[AtlasInventory, ...] = (),
    abbreviations: tuple[NeuropilAbbreviation, ...] = (),
) -> BeeBrainConnectomeReport:
    """Parse local HSB VRML archives into a structural projectome graph."""

    atlas_dir = source_dir / "virtual-honeybee-standard-brain"
    nodes: dict[str, ConnectomeNode] = {}
    edges: list[ConnectomeEdge] = []

    for entry in abbreviations[:48]:
        region = entry.region_class or "neuropil"
        node_id = f"neuropil:{entry.abbreviation.lower()}"
        nodes[node_id] = ConnectomeNode(
            node_id=node_id,
            kind="neuropil",
            label=entry.label or entry.abbreviation,
            module_target=region,
            source_asset="neuropil_abbreviations.html",
            provenance_doi=HSB_DOI,
        )

    for module, _count in _module_neuropil_counts(abbreviations).items():
        module_id = f"neuropil:{module}"
        if module_id not in nodes:
            nodes[module_id] = ConnectomeNode(
                node_id=module_id,
                kind="neuropil",
                label=module.replace("_", " "),
                module_target=module,
                source_asset="neuropil_abbreviations.html",
                provenance_doi=HSB_DOI,
            )

    asset_by_id = {asset.asset_id: asset for asset in honeybee_standard_brain_assets()}
    inventory_by_file = {Path(inventory.local_path).name: inventory for inventory in inventories}

    for asset_id, module_hint in ASSET_MODULE_HINTS.items():
        asset = asset_by_id.get(asset_id)
        if asset is None:
            continue
        zip_path = atlas_dir / asset.file_name
        if not zip_path.exists():
            continue
        vrml_names = _vrml_def_names_from_zip(zip_path)
        for name in sorted(vrml_names)[:24]:
            node_id = f"neuron:{asset_id}:{name.lower()}"
            nodes[node_id] = ConnectomeNode(
                node_id=node_id,
                kind="neuron" if "tract" not in name.lower() else "tract",
                label=name,
                module_target=module_hint,
                source_asset=asset.file_name,
                provenance_doi=HSB_DOI,
            )
        inventory = inventory_by_file.get(asset.file_name)
        if inventory is not None and inventory.vrml_count:
            tract_id = f"tract:{asset_id}"
            nodes[tract_id] = ConnectomeNode(
                node_id=tract_id,
                kind="tract",
                label=f"{asset.title} tract bundle",
                module_target=module_hint,
                source_asset=asset.file_name,
                provenance_doi=HSB_DOI,
            )

    for edge_id, source, target, evidence in STRUCTURAL_PATHWAYS:
        if source not in nodes:
            nodes[source] = ConnectomeNode(
                node_id=source,
                kind="neuropil",
                label=source.split(":", 1)[-1].replace("_", " "),
                module_target=source.split(":", 1)[-1],
                source_asset="pathway_semantics",
                provenance_doi=HSB_DOI,
            )
        if target not in nodes:
            nodes[target] = ConnectomeNode(
                node_id=target,
                kind="neuropil",
                label=target.split(":", 1)[-1].replace("_", " "),
                module_target=target.split(":", 1)[-1],
                source_asset="pathway_semantics",
                provenance_doi=HSB_DOI,
            )
        edges.append(
            ConnectomeEdge(
                source_id=source,
                target_id=target,
                edge_kind="structural_tract",
                weight=None,
                evidence=evidence,
            )
        )
        tract_node = f"tract:{edge_id}"
        if tract_node not in nodes:
            nodes[tract_node] = ConnectomeNode(
                node_id=tract_node,
                kind="tract",
                label=edge_id.replace("-", " "),
                module_target=nodes[source].module_target,
                source_asset="pathway_semantics",
                provenance_doi=HSB_DOI,
            )
        edges.append(
            ConnectomeEdge(
                source_id=tract_node,
                target_id=target,
                edge_kind="structural_tract",
                weight=None,
                evidence=f"{evidence} (tract node)",
            )
        )

    structural_edge_count = sum(1 for edge in edges if edge.edge_kind == "structural_tract")
    synaptic_edge_count = sum(1 for edge in edges if edge.edge_kind == "synaptic")
    completeness = {
        "structural_coverage": min(1.0, structural_edge_count / max(1, len(STRUCTURAL_PATHWAYS))),
        "functional_coverage": 0.0,
        "synaptic_coverage": 0.0 if synaptic_edge_count == 0 else float(synaptic_edge_count),
        "neuropil_node_fraction": min(1.0, len(abbreviations) / 40.0) if abbreviations else 0.0,
    }
    tier: ConnectomeTier = (
        "structural_projectome" if structural_edge_count else "synaptic_unavailable"
    )
    return BeeBrainConnectomeReport(
        tier=tier,
        nodes=tuple(sorted(nodes.values(), key=lambda node: node.node_id)),
        edges=tuple(edges),
        completeness=completeness,
    )


def connectome_tiers_from_report(report: BeeBrainConnectomeReport) -> dict[str, object]:
    """Summarize structural / functional / synaptic tiers for completeness JSON."""

    structural_edges = sum(1 for edge in report.edges if edge.edge_kind == "structural_tract")
    functional_edges = sum(1 for edge in report.edges if edge.edge_kind == "functional_granger")
    synaptic_edges = sum(1 for edge in report.edges if edge.edge_kind == "synaptic")
    return {
        "structural": {
            "tier": "structural_projectome",
            "available": structural_edges > 0,
            "edge_count": structural_edges,
            "coverage": report.completeness.get("structural_coverage", 0.0),
        },
        "functional": {
            "tier": "functional_partial" if functional_edges else "unavailable",
            "available": functional_edges > 0,
            "edge_count": functional_edges,
            "coverage": report.completeness.get("functional_coverage", 0.0),
            "blocker": None
            if functional_edges
            else "VAR_connectivity matrix not public; authors provide data on request",
        },
        "synaptic": {
            "tier": "synaptic_unavailable",
            "available": False,
            "edge_count": synaptic_edges,
            "coverage": 0.0,
            "blocker": "no public whole-brain Apis mellifera synaptic connectome",
        },
    }


def _module_neuropil_counts(
    abbreviations: tuple[NeuropilAbbreviation, ...],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in abbreviations:
        region = entry.region_class or "neuropil"
        counts[region] = counts.get(region, 0) + 1
    return counts


def _vrml_def_names_from_zip(zip_path: Path) -> set[str]:
    names: set[str] = set()
    with zipfile.ZipFile(zip_path) as archive:
        validate_zip_archive_bounds(archive)
        for info in archive.infolist():
            if info.is_dir():
                continue
            assert_safe_zip_member(info.filename)
            if not info.filename.lower().endswith((".wrl", ".vrml")):
                continue
            text = archive.read(info.filename)[:2_000_000].decode("utf-8", "ignore")
            names.update(re.findall(r"\bDEF\s+([A-Za-z0-9_\-]+)", text))
            names.update(re.findall(r"\bUSE\s+([A-Za-z0-9_\-]+)", text))
    return {name for name in names if name and name.lower() not in {"scene", "world"}}
