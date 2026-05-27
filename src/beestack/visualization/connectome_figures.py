"""Connectome figures for BeeBrain structural wiring evidence."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.patches import FancyArrowPatch

from ..brain.connectome import BeeBrainConnectomeReport
from .figure_output import finalize_static_figures
from .figure_plot_specs import connectome_plot_data
from .style import (
    add_figure_note,
    add_status_badge,
    apply_panel_style,
    bounded_text,
    status_color,
    style_context,
)


def generate_connectome_figures(
    report: BeeBrainConnectomeReport,
    output_dir: Path,
    *,
    completeness_tiers: dict[str, object] | None = None,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    context = {"report": report, "tiers": completeness_tiers or {}}
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
        return {
            "title": path.stem.replace("_", " ").title(),
            "backend": "matplotlib/networkx connectome renderer",
            "fidelity": "Honeybee Standard Brain structural projectome diagnostic",
            "source_data": "output/data/bee_brain_connectome.json",
            "validation_status": "structural connectome tier witness with plot data",
            "regeneration_command": "uv run python scripts/analyze_empirical_bee_data.py",
        }

    finalize_static_figures(paths, plot_data_for=_plot_data, sidecar_for=_sidecar)
    return paths


def _structural_graph(report: BeeBrainConnectomeReport, path: Path) -> Path:
    graph = nx.DiGraph()
    for node in report.nodes:
        graph.add_node(
            node.node_id,
            label=node.label,
            kind=node.kind,
            module_target=node.module_target,
        )
    for edge in report.edges:
        if edge.edge_kind == "structural_tract":
            graph.add_edge(edge.source_id, edge.target_id, evidence=edge.evidence)
    fig, ax = plt.subplots(figsize=(9.8, 6.2))
    ax.axis("off")
    ax.set_title("BeeBrain structural projectome (HSB VRML)", loc="left", pad=12)
    add_status_badge(
        ax,
        "structural projectome only",
        status="structural",
        xy=(0.03, 0.93),
        width=28,
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
            s=980 + count * 16,
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
    pathway_labels = {
        ("antennal_lobe", "mushroom_body"): "ALF1",
        ("antennal_lobe", "central_complex"): "ACT",
        ("mushroom_body", "central_complex"): "Pe1/Pn",
    }
    drawn: set[tuple[str, str]] = set()
    for source, target in graph.edges:
        source_cluster = _cluster_for_node(source, graph)
        target_cluster = _cluster_for_node(target, graph)
        if source_cluster not in positions or target_cluster not in positions:
            continue
        edge_key = (source_cluster, target_cluster)
        if edge_key in drawn or source_cluster == target_cluster:
            continue
        drawn.add(edge_key)
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
                color="#334155",
                alpha=0.78,
                connectionstyle="arc3,rad=0.08",
                zorder=2,
            )
        )
        label = pathway_labels.get(edge_key, "tract")
        ax.text(
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2 + 0.035,
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
            f"Report inventory: {graph.number_of_nodes()} nodes, "
            f"{graph.number_of_edges()} structural tract edges. Labels are "
            "clustered by BeeBrain module to keep manuscript-scale topology readable."
        ),
        width=44,
        max_lines=5,
    )
    bounded_text(
        ax,
        0.03,
        0.23,
        "Boundary: no synaptic adjacency, no functional Granger completeness, and no calcium-validated dynamics are inferred from the structural paths.",
        width=44,
        max_lines=5,
        facecolor="#FFF7ED",
        edgecolor="#FED7AA",
    )
    add_figure_note(
        fig,
        "HSB structural pathways are shown as top-level witnesses; detailed node inventories remain in output/data/bee_brain_connectome.json and plot-data sidecars.",
        y=0.02,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _neuropil_module_map(report: BeeBrainConnectomeReport, path: Path) -> Path:
    counts = Counter(node.module_target for node in report.nodes if node.kind == "neuropil")
    modules = sorted(counts)
    values = [counts[module] for module in modules]
    fig, ax = plt.subplots(figsize=(7, 4))
    apply_panel_style(ax, title="Neuropil abbreviations by BeeBrain module")
    ax.imshow(np.array([values], dtype=float), aspect="auto", cmap="YlGnBu")
    ax.set_xticks(range(len(modules)))
    ax.set_xticklabels(modules, rotation=35, ha="right", fontsize=8)
    ax.set_yticks([])
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
    coverage = [
        float((tiers.get(label, {}) or {}).get("coverage", report.completeness.get(f"{label}_coverage", 0.0)))
        for label in labels
    ]
    fig, ax = plt.subplots(figsize=(6, 4))
    apply_panel_style(ax, title="Connectome evidence tiers")
    colors = [
        status_color("structural"),
        status_color("partial"),
        status_color("unavailable"),
    ]
    bars = ax.bar(labels, coverage, color=colors)
    for bar, value in zip(bars, coverage, strict=True):
        status = "available" if value > 0 else "unavailable"
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            max(0.04, value + 0.035),
            f"{status}\n{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=8,
            color="#111827",
        )
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("coverage fraction")
    bounded_text(
        ax,
        0.02,
        0.96,
        "Structural tier is a projectome witness; unavailable tiers stay explicit rather than filled.",
        width=38,
        max_lines=3,
        fontsize=8,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _cluster_counts(graph: nx.DiGraph) -> Counter[str]:
    counts: Counter[str] = Counter()
    for node in graph.nodes:
        counts[_cluster_for_node(node, graph)] += 1
    return counts


def _cluster_for_node(node: str, graph: nx.DiGraph) -> str:
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
