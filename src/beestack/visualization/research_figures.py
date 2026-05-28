"""Research-suite figures and interactive outputs."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, Rectangle

from .figure_metadata import assert_nonblank_quality
from .figure_output import finalize_static_figures, write_stable_plotly_html
from .figure_plot_specs import research_plot_data
from .style import (
    add_figure_note,
    apply_panel_style,
    bounded_text,
    module_color,
    status_color,
    style_context,
    wrap_label,
)

if TYPE_CHECKING:
    from ..research import ResearchSuiteReport


def generate_research_figures(report: ResearchSuiteReport, output_dir: Path) -> list[Path]:
    """Generate science-first research report figures."""

    output_dir.mkdir(parents=True, exist_ok=True)
    with style_context():
        paths = [
            _scorecard_heatmap(report, output_dir / "research_module_scorecard_heatmap.png"),
            _validation_bars(report, output_dir / "research_validation_scorecard.png"),
            _sensitivity_sweeps(report, output_dir / "research_sensitivity_sweeps.png"),
            _evidence_network(report, output_dir / "research_fidelity_evidence_network.png"),
            _evidence_detail(report, output_dir / "research_evidence_detail.png"),
            _visualization_inventory(report, output_dir / "research_visualization_inventory.png"),
            _empirical_completeness(report, output_dir / "research_empirical_completeness.png"),
            _module_metric_bars(report, "BeeBody", output_dir / "beebody_method_diagnostics.png"),
            _module_metric_bars(
                report, "BeeBrain", output_dir / "beebrain_empirical_evidence_map.png"
            ),
            _module_metric_bars(report, "BeeMind", output_dir / "beemind_policy_sensitivity.png"),
            _module_metric_bars(
                report, "BeeSwarm", output_dir / "beeswarm_contact_recruitment_scorecard.png"
            ),
            _module_metric_bars(
                report, "BeeNiche", output_dir / "beeniche_thermal_comb_scorecard.png"
            ),
        ]
    for path in paths:
        _validate_nonblank_image(path)

    def _plot_data(path: Path) -> dict[str, object]:
        return research_plot_data(path, report=report)

    def _sidecar(path: Path) -> dict[str, object]:
        return {
            "title": path.stem.replace("_", " ").title(),
            "backend": "Matplotlib/pandas/NetworkX",
            "fidelity": _research_figure_fidelity(path.name),
            "source_data": "ResearchSuiteReport scorecards, evidence records, sweeps, and visual inventory",
            "validation_status": "nonblank image, quality sidecar, and plot data passed",
            "regeneration_command": "uv run python scripts/run_research_suite.py",
        }

    finalize_static_figures(paths, plot_data_for=_plot_data, sidecar_for=_sidecar)
    return paths


def _research_figure_fidelity(filename: str) -> str:
    """Classify research-suite figures by evidence tier."""

    if "empirical" in filename or "beebrain" in filename:
        return "empirical summary projected into reduced BeeBrain contracts"
    if "beebody" in filename:
        return "FlyBody-backed render diagnostics plus reduced telemetry"
    if "network" in filename or "inventory" in filename or "scorecard" in filename:
        return "research provenance diagnostic"
    return "reduced deterministic kernel diagnostic"


def write_interactive_research_outputs(report: ResearchSuiteReport, output_dir: Path) -> list[Path]:
    """Write optional Plotly HTML research outputs."""

    import plotly.express as px

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
    write_stable_plotly_html(fig, scorecard_path)

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
    write_stable_plotly_html(fig, sweep_path)
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
    fig, ax = plt.subplots(figsize=(10.5, 5.9))
    image = ax.imshow(normalized.to_numpy(), aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_title("BeeStack dense research method scorecard", loc="left")
    ax.set_xticks(
        range(len(normalized.columns)),
        [
            wrap_label(column.replace("_", " "), width=16, max_lines=2)
            for column in normalized.columns
        ],
        rotation=20,
        ha="right",
    )
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
    bounded_text(
        ax,
        0.02,
        -0.24,
        "Read as a provenance scorecard: normalized cells support gap visibility and readiness review, not biological predictive validation.",
        width=96,
        max_lines=2,
        fontsize=8,
    )
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
    ax.bar(
        frame["module"],
        frame["validation_fraction"],
        color=[module_color(module) for module in frame["module"]],
    )
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Validation fraction")
    ax.set_title("Research-suite validation scorecard")
    apply_panel_style(ax, grid_axis="y")
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
    positions = {
        "BeeBody": (0.16, 0.68),
        "BeeBrain": (0.38, 0.74),
        "BeeMind": (0.60, 0.68),
        "BeeSwarm": (0.28, 0.34),
        "BeeNiche": (0.50, 0.34),
    }
    evidence_counts = {
        scorecard.module: len(scorecard.evidence) for scorecard in report.module_scorecards
    }
    gap_counts = {
        scorecard.module: len(scorecard.known_gaps) for scorecard in report.module_scorecards
    }
    fig, ax = plt.subplots(figsize=(10.2, 6.4))
    ax.axis("off")
    ax.set_title("BeeStack evidence network overview", loc="left", pad=12)
    for scorecard in report.module_scorecards:
        x, y = positions.get(scorecard.module, (0.5, 0.5))
        radius = 950 + evidence_counts[scorecard.module] * 90
        ax.scatter(
            [x],
            [y],
            s=radius,
            color=module_color(scorecard.module),
            edgecolor="#111827",
            linewidth=1.0,
            alpha=0.92,
            transform=ax.transAxes,
            zorder=3,
        )
        ax.text(
            x,
            y + 0.01,
            scorecard.module,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=9.2,
            fontweight="bold",
            color="white",
            zorder=4,
        )
        ax.text(
            x,
            y - 0.095,
            f"{evidence_counts[scorecard.module]} evidence\n{gap_counts[scorecard.module]} gaps",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=8,
            color="#334155",
        )
    for source, target in (
        ("BeeBody", "BeeBrain"),
        ("BeeBrain", "BeeMind"),
        ("BeeMind", "BeeSwarm"),
        ("BeeSwarm", "BeeNiche"),
        ("BeeNiche", "BeeBody"),
    ):
        if source not in positions or target not in positions:
            continue
        ax.add_patch(
            FancyArrowPatch(
                positions[source],
                positions[target],
                transform=ax.transAxes,
                arrowstyle="-|>",
                mutation_scale=14,
                lw=1.2,
                color="#64748B",
                alpha=0.65,
                connectionstyle="arc3,rad=0.10",
                zorder=1,
            )
        )
    empirical_count = len(report.empirical_evidence)
    bounded_text(
        ax,
        0.70,
        0.78,
        f"Empirical records route to BeeBrain: {empirical_count}. Detail companion lists source rows and integration targets.",
        width=38,
        max_lines=4,
        fontsize=8.4,
        facecolor="#F8FAFC",
    )
    bounded_text(
        ax,
        0.70,
        0.42,
        "Boundary: edge arrows show provenance routing and reduced-stack handoff, not predictive biological validation.",
        width=38,
        max_lines=4,
        fontsize=8.4,
        facecolor="#FFF7ED",
        edgecolor="#FED7AA",
    )
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _evidence_detail(report: ResearchSuiteReport, path: Path) -> Path:
    rows: list[dict[str, str]] = []
    for scorecard in report.module_scorecards:
        rows.append(
            {
                "module": scorecard.module,
                "kind": "scorecard",
                "item": "; ".join(scorecard.evidence[:2]),
                "status": f"{scorecard.validation_fraction:.2f} validation",
                "boundary": "; ".join(scorecard.known_gaps[:2])
                or "explicit gaps carried in report",
            }
        )
    for record in report.empirical_evidence:
        rows.append(
            {
                "module": "BeeBrain",
                "kind": "empirical",
                "item": record.dataset_id,
                "status": record.availability_status,
                "boundary": record.integration_target,
            }
        )
    fig, ax = plt.subplots(figsize=(12.2, 6.6))
    ax.axis("off")
    ax.text(
        0.02,
        0.96,
        "Research evidence detail: scorecards and empirical routing",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=13,
        fontweight="bold",
        color="#111827",
    )
    headers = ("Module", "Kind", "Evidence item", "Status", "Boundary / target")
    x_positions = (0.02, 0.13, 0.25, 0.55, 0.70)
    for header, x in zip(headers, x_positions, strict=True):
        ax.text(x, 0.86, header, transform=ax.transAxes, fontsize=8.5, fontweight="bold")
    for index, row in enumerate(rows[:12]):
        y = 0.80 - index * 0.060
        ax.add_patch(
            Rectangle(
                (0.015, y - 0.025),
                0.96,
                0.050,
                transform=ax.transAxes,
                facecolor="#F8FAFC" if index % 2 == 0 else "#FFFFFF",
                edgecolor="#E2E8F0",
                lw=0.5,
            )
        )
        ax.text(
            x_positions[0],
            y,
            row["module"],
            transform=ax.transAxes,
            va="center",
            fontsize=8.2,
            color=module_color(row["module"]) if row["module"].startswith("Bee") else "#334155",
            fontweight="bold",
        )
        ax.text(x_positions[1], y, row["kind"], transform=ax.transAxes, va="center", fontsize=8.0)
        ax.text(
            x_positions[2],
            y,
            wrap_label(row["item"], width=34, max_lines=2),
            transform=ax.transAxes,
            va="center",
            fontsize=7.5,
            color="#111827",
        )
        ax.text(
            x_positions[3],
            y,
            wrap_label(row["status"], width=18, max_lines=2),
            transform=ax.transAxes,
            va="center",
            fontsize=7.5,
            color="#334155",
        )
        ax.text(
            x_positions[4],
            y,
            wrap_label(row["boundary"], width=38, max_lines=2),
            transform=ax.transAxes,
            va="center",
            fontsize=7.5,
            color="#334155",
        )
    add_figure_note(
        fig,
        "Detail companion to the evidence-network overview; rows are provenance and availability witnesses only.",
        y=0.018,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _visualization_inventory(report: ResearchSuiteReport, path: Path) -> Path:
    frame = pd.DataFrame([artifact.as_dict() for artifact in report.visualization_artifacts])
    counts = frame.groupby(["artifact_type", "fidelity_level"]).size().reset_index(name="count")
    labels = [f"{row.artifact_type}\n{row.fidelity_level}" for row in counts.itertuples()]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(labels[::-1], counts["count"].to_numpy()[::-1], color=module_color("BeeBody"))
    ax.set_xlabel("Artifact count")
    ax.set_title("Visualization artifact inventory by fidelity")
    apply_panel_style(ax, grid_axis="x")
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _empirical_completeness(report: ResearchSuiteReport, path: Path) -> Path:
    frame = pd.DataFrame([evidence.as_dict() for evidence in report.empirical_evidence])
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(
        frame["dataset_id"][::-1],
        frame["completeness_fraction"][::-1],
        color=module_color("BeeBrain"),
    )
    for bar, fraction in zip(bars, frame["completeness_fraction"][::-1], strict=False):
        status = "available" if float(fraction) >= 0.8 else "partial"
        ax.text(
            min(0.98, float(fraction) + 0.02),
            bar.get_y() + bar.get_height() / 2,
            f"{float(fraction):.2f} {status}",
            va="center",
            ha="left",
            fontsize=7.8,
            color="#111827",
        )
    ax.set_xlim(0, 1)
    ax.set_xlabel("Completeness fraction")
    ax.set_title("BeeBrain empirical evidence completeness")
    ax.axvline(0.8, color=status_color("warning"), lw=0.9, ls="--")
    apply_panel_style(ax, grid_axis="x")
    add_figure_note(
        fig,
        "Completeness is source availability and parseability; it does not fill blocked calcium or synaptic evidence.",
        y=0.012,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _module_metric_bars(report: ResearchSuiteReport, module: str, path: Path) -> Path:
    scorecard = next(item for item in report.module_scorecards if item.module == module)
    labels = list(scorecard.metrics)
    values = [scorecard.metrics[label] for label in labels]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(
        [wrap_label(label.replace("_", " "), width=28, max_lines=2) for label in labels[::-1]],
        values[::-1],
        color=module_color(module),
    )
    ax.set_title(f"{module} research diagnostics")
    apply_panel_style(ax, grid_axis="x")
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _validate_nonblank_image(path: Path) -> None:
    assert_nonblank_quality(path)
