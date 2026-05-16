"""Research-suite figures and interactive outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
from skimage import io as skio
from skimage.measure import label

from ..research import ResearchSuiteReport


def generate_research_figures(report: ResearchSuiteReport, output_dir: Path) -> list[Path]:
    """Generate science-first research report figures."""

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        _scorecard_heatmap(report, output_dir / "research_module_scorecard_heatmap.png"),
        _validation_bars(report, output_dir / "research_validation_scorecard.png"),
        _sensitivity_sweeps(report, output_dir / "research_sensitivity_sweeps.png"),
        _evidence_network(report, output_dir / "research_fidelity_evidence_network.png"),
        _visualization_inventory(report, output_dir / "research_visualization_inventory.png"),
        _empirical_completeness(report, output_dir / "research_empirical_completeness.png"),
        _module_metric_bars(report, "BeeBody", output_dir / "beebody_method_diagnostics.png"),
        _module_metric_bars(report, "BeeBrain", output_dir / "beebrain_empirical_evidence_map.png"),
        _module_metric_bars(report, "BeeMind", output_dir / "beemind_policy_sensitivity.png"),
        _module_metric_bars(
            report, "BeeSwarm", output_dir / "beeswarm_contact_recruitment_scorecard.png"
        ),
        _module_metric_bars(report, "BeeNiche", output_dir / "beeniche_thermal_comb_scorecard.png"),
    ]
    for path in paths:
        _validate_nonblank_image(path)
    return paths


def write_interactive_research_outputs(report: ResearchSuiteReport, output_dir: Path) -> list[Path]:
    """Write optional Plotly HTML research outputs."""

    output_dir.mkdir(parents=True, exist_ok=True)
    scorecard_rows = [
        {
            "module": scorecard.module,
            "validation_fraction": scorecard.validation_fraction,
            "fidelity_level": scorecard.fidelity_level,
        }
        for scorecard in report.module_scorecards
    ]
    scorecard_path = output_dir / "research_scorecards.html"
    fig = px.bar(
        pd.DataFrame(scorecard_rows),
        x="module",
        y="validation_fraction",
        color="fidelity_level",
        range_y=(0, 1),
        title="BeeStack research validation scorecards",
    )
    fig.write_html(scorecard_path, include_plotlyjs="cdn")

    sweep_rows = []
    for sweep in report.sensitivity_sweeps:
        for output_name, values in sweep.outputs.items():
            for value, output in zip(sweep.values, values, strict=True):
                sweep_rows.append(
                    {
                        "parameter": sweep.parameter,
                        "value": value,
                        "output_name": output_name,
                        "output": output,
                    }
                )
    sweep_path = output_dir / "research_sensitivity_sweeps.html"
    fig = px.line(
        pd.DataFrame(sweep_rows),
        x="value",
        y="output",
        color="output_name",
        facet_col="parameter",
        facet_col_wrap=2,
        title="BeeStack reduced-kernel sensitivity sweeps",
    )
    fig.write_html(sweep_path, include_plotlyjs="cdn")
    return [scorecard_path, sweep_path]


def _scorecard_heatmap(report: ResearchSuiteReport, path: Path) -> Path:
    module_keywords = {
        "BeeBody": ("beebody", "body"),
        "BeeBrain": ("beebrain", "brain"),
        "BeeMind": ("beemind", "mind"),
        "BeeSwarm": ("beeswarm", "swarm", "waggle", "collision"),
        "BeeNiche": ("beeniche", "niche", "comb", "thermal"),
    }
    rows: list[dict[str, float | str]] = []
    for scorecard in report.module_scorecards:
        metric_values = np.asarray(tuple(scorecard.metrics.values()), dtype=float)
        artifact_count = _artifact_count_for_module(
            report, module_keywords.get(scorecard.module, (scorecard.module.lower(),))
        )
        rows.append(
            {
                "module": scorecard.module,
                "validation_fraction": scorecard.validation_fraction,
                "metric_count": float(len(metric_values)),
                "median_log_metric": float(np.median(np.log10(np.abs(metric_values) + 1.0))),
                "evidence_count": float(len(scorecard.evidence)),
                "gap_closure": 1.0 / (1.0 + len(scorecard.known_gaps)),
                "visual_artifacts": float(artifact_count),
            }
        )
    frame = pd.DataFrame(rows).set_index("module")
    normalized = frame.copy()
    for column in normalized.columns:
        values = frame[column].astype(float)
        span = float(values.max() - values.min())
        if span == 0:
            normalized[column] = 1.0 if float(values.max()) > 0 else 0.0
        else:
            normalized[column] = (values - float(values.min())) / span
    fig, ax = plt.subplots(figsize=(10, 5.8))
    image = ax.imshow(normalized.to_numpy(), aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_title("BeeStack dense research method scorecard")
    ax.set_xticks(range(len(normalized.columns)), normalized.columns, rotation=25, ha="right")
    ax.set_yticks(range(len(normalized.index)), normalized.index)
    for row_index, module in enumerate(frame.index):
        for column_index, column in enumerate(frame.columns):
            value = frame.loc[module, column]
            ax.text(
                column_index,
                row_index,
                f"{float(value):.2g}",
                ha="center",
                va="center",
                fontsize=7,
                color="white" if normalized.loc[module, column] < 0.58 else "black",
            )
    fig.colorbar(image, ax=ax, label="Column-normalized summary score")
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _artifact_count_for_module(report: ResearchSuiteReport, keywords: tuple[str, ...]) -> int:
    count = 0
    for artifact in report.visualization_artifacts:
        path_text = artifact.path.lower()
        if any(keyword in path_text for keyword in keywords):
            count += 1
    return count


def _validation_bars(report: ResearchSuiteReport, path: Path) -> Path:
    frame = pd.DataFrame(
        {
            "module": [scorecard.module for scorecard in report.module_scorecards],
            "validation_fraction": [
                scorecard.validation_fraction for scorecard in report.module_scorecards
            ],
        }
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(frame["module"], frame["validation_fraction"], color="#2a9d8f")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Validation fraction")
    ax.set_title("Research-suite validation scorecard")
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _sensitivity_sweeps(report: ResearchSuiteReport, path: Path) -> Path:
    fig, axes = plt.subplots(len(report.sensitivity_sweeps), 1, figsize=(9, 8), sharex=False)
    axes = np.atleast_1d(axes)
    for axis, sweep in zip(axes, report.sensitivity_sweeps, strict=True):
        for output_name, values in sweep.outputs.items():
            axis.plot(sweep.values, values, marker="o", label=output_name)
        axis.set_title(sweep.parameter)
        axis.grid(alpha=0.22)
        axis.legend(fontsize=7, ncol=2)
    fig.suptitle("Reduced-kernel sensitivity sweeps", y=0.995)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _evidence_network(report: ResearchSuiteReport, path: Path) -> Path:
    graph = nx.DiGraph()
    for scorecard in report.module_scorecards:
        graph.add_node(scorecard.module, kind="module")
        for evidence in scorecard.evidence:
            evidence_node = f"{scorecard.module}:evidence"
            graph.add_node(evidence_node, kind="evidence")
            graph.add_edge(scorecard.module, evidence_node, label=evidence[:24])
    for evidence in report.empirical_evidence:
        graph.add_node(evidence.dataset_id, kind="empirical")
        graph.add_edge(evidence.dataset_id, "BeeBrain", label=evidence.integration_target)
    positions = nx.spring_layout(graph, seed=13)
    colors = [
        "#f59e0b"
        if graph.nodes[node]["kind"] == "module"
        else "#2563eb"
        if graph.nodes[node]["kind"] == "empirical"
        else "#94a3b8"
        for node in graph.nodes
    ]
    fig, ax = plt.subplots(figsize=(10, 7))
    nx.draw_networkx_edges(graph, positions, ax=ax, alpha=0.35, arrows=True)
    nx.draw_networkx_nodes(graph, positions, node_color=colors, node_size=1050, ax=ax)
    nx.draw_networkx_labels(graph, positions, font_size=7, ax=ax)
    ax.set_title("BeeStack fidelity and empirical evidence network")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _visualization_inventory(report: ResearchSuiteReport, path: Path) -> Path:
    frame = pd.DataFrame([artifact.as_dict() for artifact in report.visualization_artifacts])
    counts = frame.groupby(["artifact_type", "fidelity_level"]).size().reset_index(name="count")
    labels = [f"{row.artifact_type}\n{row.fidelity_level}" for row in counts.itertuples()]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(labels[::-1], counts["count"].to_numpy()[::-1], color="#d99a28")
    ax.set_xlabel("Artifact count")
    ax.set_title("Visualization artifact inventory by fidelity")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _empirical_completeness(report: ResearchSuiteReport, path: Path) -> Path:
    frame = pd.DataFrame([evidence.as_dict() for evidence in report.empirical_evidence])
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(frame["dataset_id"][::-1], frame["completeness_fraction"][::-1], color="#3a6ea5")
    ax.set_xlim(0, 1)
    ax.set_xlabel("Completeness fraction")
    ax.set_title("BeeBrain empirical evidence completeness")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _module_metric_bars(report: ResearchSuiteReport, module: str, path: Path) -> Path:
    scorecard = next(item for item in report.module_scorecards if item.module == module)
    labels = list(scorecard.metrics)
    values = [scorecard.metrics[label] for label in labels]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(labels[::-1], values[::-1], color="#5b8e7d")
    ax.set_title(f"{module} research diagnostics")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _validate_nonblank_image(path: Path) -> None:
    image = skio.imread(path)
    if image.size == 0:
        raise ValueError(f"{path} is empty")
    grayscale = image[..., :3].mean(axis=2) if image.ndim == 3 else image
    foreground = np.abs(grayscale.astype(float) - float(np.median(grayscale))) > 1.0
    if int(label(foreground).max()) <= 0:
        raise ValueError(f"{path} appears blank")
