"""Connectome figures for BeeBrain structural wiring evidence."""

from __future__ import annotations

from collections import Counter
from dataclasses import replace
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch

from ..brain.connectome import BeeBrainConnectomeReport
from .figure_output import finalize_static_figures
from .figure_plot_specs import (
    connectome_coverage,
    connectome_fidelity,
    connectome_graph,
    connectome_plot_data,
)
from .figure_registry import figure_narrative_for_path
from .style import (
    add_figure_note,
    add_status_badge,
    apply_panel_style,
    bounded_text,
    status_color,
    style_context,
    wrap_label,
)


def generate_connectome_figures(
    report: BeeBrainConnectomeReport,
    output_dir: Path,
    *,
    completeness_tiers: dict[str, object] | None = None,
    project_root: Path | None = None,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    context = {"report": report, "tiers": completeness_tiers or {}}
    evidence = connectome_fidelity(report)
    with style_context():
        paths = [
            _structural_graph(report, output_dir / "connectome_structural_graph.png"),
            _neuropil_module_map(report, output_dir / "connectome_neuropil_module_map.png"),
            _completeness_tiers(
                report,
                completeness_tiers or {},
                output_dir / "connectome_completeness_tiers.png",
            ),
        ]

    def _plot_data(path: Path) -> dict[str, object]:
        return connectome_plot_data(
            path,
            report=report,
            completeness_tiers=context["tiers"],
        )

    def _sidecar(path: Path) -> dict[str, object]:
        narrative = figure_narrative_for_path(path)
        assert narrative is not None
        title = evidence["title"] if path.stem == "connectome_structural_graph" else narrative.title
        runtime = replace(
            narrative,
            title=title,
            caption=f"{narrative.caption} {evidence['summary']}",
            alt_text=f"{narrative.alt_text} {evidence['summary']}",
            claim_tier=evidence["claim_tier"],
            fidelity_level=evidence["fidelity"],
        )
        return {
            **runtime.as_sidecar_fields(),
            "title": title,
            "backend": "matplotlib/networkx connectome renderer",
            "fidelity": evidence["fidelity"],
            "source_data": "output/data/bee_brain_connectome.json",
            "validation_status": evidence["summary"],
            "regeneration_command": "uv run python scripts/analyze_empirical_bee_data.py",
            "metrics": {
                key: evidence[key]
                for key in ("tier", "evidence_state", "edge_counts", "supporting_assets")
            },
        }

    finalize_static_figures(
        paths, plot_data_for=_plot_data, sidecar_for=_sidecar, project_root=project_root
    )
    return paths


def _structural_graph(report: BeeBrainConnectomeReport, path: Path) -> Path:
    fig = _structural_graph_figure(report)
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _structural_graph_figure(report: BeeBrainConnectomeReport) -> Figure:
    graph = connectome_graph(report)
    evidence = connectome_fidelity(report)
    fig, ax = plt.subplots(figsize=(11.2, 7.2))
    ax.axis("off")
    ax.set_title(wrap_label(evidence["title"], width=78), loc="left", pad=14)
    add_status_badge(
        ax,
        evidence["evidence_state"].replace("_", " "),
        status="structural" if evidence["evidence_state"] == "structural_projectome" else "partial",
        xy=(0.03, 0.93),
        width=36,
    )
    positions = {
        "antennal_lobe": (0.18, 0.62),
        "mushroom_body": (0.47, 0.74),
        "central_complex": (0.48, 0.38),
        "whole_brain": (0.76, 0.56),
    }
    module_labels = {
        "antennal_lobe": "AL",
        "mushroom_body": "MB",
        "central_complex": "CX",
        "whole_brain": "WB",
    }
    cluster_counts = _cluster_counts(graph)
    for cluster, (x, y) in positions.items():
        count = cluster_counts.get(cluster, 0)
        ax.scatter(
            [x],
            [y],
            s=1500,
            color=status_color("structural"),
            alpha=0.90,
            edgecolor="#111827",
            linewidth=1.0,
            transform=ax.transAxes,
            zorder=3,
        )
        ax.text(
            x,
            y + 0.005,
            module_labels[cluster],
            transform=ax.transAxes,
            ha="center",
            va="center",
            color="white",
            fontsize=14,
            fontweight="bold",
            zorder=4,
        )
        ax.text(
            x,
            y - 0.085,
            f"{cluster.replace('_', ' ')}\n{count} nodes",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=8.2,
            color="#334155",
        )
    cluster_edges = Counter(
        (_cluster_for_node(source, graph), _cluster_for_node(target, graph), data["edge_kind"])
        for source, target, data in graph.edges(data=True)
        if _cluster_for_node(source, graph) != _cluster_for_node(target, graph)
    )
    drawn: set[tuple[str, str, str]] = set()
    for source, target, data in graph.edges(data=True):
        source_cluster = _cluster_for_node(source, graph)
        target_cluster = _cluster_for_node(target, graph)
        if source_cluster not in positions or target_cluster not in positions:
            continue
        edge_key = (source_cluster, target_cluster)
        kind = data["edge_kind"]
        drawn_key = (*edge_key, kind)
        if drawn_key in drawn or source_cluster == target_cluster:
            continue
        drawn.add(drawn_key)
        schematic = kind == "schematic_pathway"
        radius = -0.12 if schematic else 0.12
        start = positions[source_cluster]
        end = positions[target_cluster]
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                transform=ax.transAxes,
                arrowstyle="-|>",
                mutation_scale=16,
                lw=2.0,
                linestyle="--" if schematic else "-",
                color="#B45309" if schematic else "#334155",
                alpha=0.78,
                connectionstyle=f"arc3,rad={radius}",
                zorder=2,
            )
        )
        edge_count = cluster_edges[drawn_key]
        kind_label = (
            "VRML-supported structural" if kind == "structural_tract" else kind.replace("_", " ")
        )
        label = f"{edge_count} {kind_label} edge(s)"
        ax.text(
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2 + (-0.045 if schematic else 0.055),
            label,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="#111827",
            bbox={
                "boxstyle": "round,pad=0.20",
                "facecolor": "#F8FAFC",
                "edgecolor": "#CBD5E1",
                "linewidth": 0.7,
            },
            zorder=5,
        )
    bounded_text(
        ax,
        0.64,
        0.23,
        (
            f"Report inventory: {graph.number_of_nodes()} nodes; "
            f"{evidence['edge_counts']['structural_tract']} supported structural edges; "
            f"{evidence['edge_counts']['schematic_pathway']} schematic edges. "
            "Links aggregate inter-module edges; internal edges remain in the source report. Dashed = schematic; other links retain their reported kind."
        ),
        width=44,
        max_lines=6,
    )
    bounded_text(
        ax,
        0.03,
        0.23,
        "Boundary: schematic paths are not observed tracts. No synaptic adjacency, functional Granger completeness, or calcium-validated dynamics are inferred.",
        width=44,
        max_lines=5,
        facecolor="#FFF7ED",
        edgecolor="#FED7AA",
    )
    add_figure_note(
        fig,
        "Pathway topology is grouped by module, not measured spatial geometry. Full edge kinds and evidence remain in the graph report and plot-data sidecars.",
        y=0.02,
    )
    fig.tight_layout()
    return fig


def _neuropil_module_map(report: BeeBrainConnectomeReport, path: Path) -> Path:
    counts = Counter(node.module_target for node in report.nodes if node.kind == "neuropil")
    modules = sorted(counts)
    values = [counts[module] for module in modules]
    fig, ax = plt.subplots(figsize=(8.5, max(4, 0.52 * len(modules) + 1.3)))
    bars = ax.barh(
        [wrap_label(module.replace("_", " "), width=34) for module in modules],
        values,
        color=status_color("structural"),
    )
    ax.bar_label(bars, fmt="%g", padding=4)
    ax.margins(x=0.18)
    apply_panel_style(
        ax,
        title="Graph neuropil-node inventory by module",
        xlabel="Registered neuropil-node count (not neural coverage)",
        grid_axis="x",
    )
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _completeness_tiers(
    report: BeeBrainConnectomeReport,
    tiers: dict[str, object],
    path: Path,
) -> Path:
    labels = ["structural", "functional", "synaptic"]
    coverage = connectome_coverage(report, tiers)
    rows = []
    for label, value in zip(labels, coverage, strict=True):
        record = tiers.get(label, {}) or {}
        state = record.get("tier") if isinstance(record, dict) else None
        if state is None and label == "structural":
            state = connectome_fidelity(report)["evidence_state"]
        rows.append(
            [
                label.capitalize(),
                "Unreported" if value is None else f"{value:.3g}",
                wrap_label(str(state or "State not supplied"), width=40),
            ]
        )
    fig, ax = plt.subplots(figsize=(9.8, 4.6))
    ax.axis("off")
    ax.set_title("Connectome source-evidence tiers", loc="left", pad=16)
    table = ax.table(
        cellText=rows,
        colLabels=["Evidence tier", "Coverage fraction", "Reported evidence state"],
        colWidths=[0.23, 0.23, 0.54],
        cellLoc="left",
        bbox=(0, 0.08, 1, 0.78),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    add_figure_note(
        fig,
        "Coverage is the report's source-evidence inventory, not measured neural completeness. Schematic paths do not count as structural tracts; explicit zero and unreported coverage remain distinct.",
        y=0.02,
    )
    fig.tight_layout(rect=(0, 0.08, 1, 0.98))
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _cluster_counts(graph: nx.MultiDiGraph) -> Counter[str]:
    counts: Counter[str] = Counter()
    for node in graph.nodes:
        counts[_cluster_for_node(node, graph)] += 1
    return counts


def _cluster_for_node(node: str, graph: nx.MultiDiGraph) -> str:
    node_text = node.lower()
    module = str(graph.nodes[node].get("module_target", "")).lower()
    merged = f"{node_text} {module}"
    if "antennal" in merged or "olfactory" in merged:
        return "antennal_lobe"
    if "mushroom" in merged:
        return "mushroom_body"
    if "central_complex" in merged or "central complex" in merged:
        return "central_complex"
    return "whole_brain"
