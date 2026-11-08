"""Methods-analysis figures and interactive dashboards."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .figure_metadata import assert_nonblank_quality
from .figure_output import finalize_static_figures, write_stable_plotly_html
from .figure_plot_specs import methods_plot_data
from .figure_registry import figure_narrative_for_path
from .figures_common import _nullable_series
from .style import (
    PALETTE,
    add_figure_note,
    add_panel_label,
    apply_panel_style,
    module_color,
    style_context,
    wrap_label,
)

if TYPE_CHECKING:
    from ..research import MethodsAnalysisReport


def generate_methods_figures(
    report: MethodsAnalysisReport,
    records: tuple[dict[str, Any], ...],
    output_dir: Path,
    *,
    project_root: Path | None = None,
) -> list[Path]:
    """Generate publication-oriented methods-analysis figures."""

    output_dir.mkdir(parents=True, exist_ok=True)
    with style_context():
        paths = [
            _repo_methods_dashboard(report, output_dir / "methods_repo_dashboard.png"),
            _methods_dashboard_detail(report, output_dir / "methods_dashboard_detail.png"),
            _body_telemetry(
                records, report, output_dir / "beebody_methods_telemetry_dashboard.png"
            ),
            _module_metric_panel(
                report,
                "BeeBrain",
                output_dir / "beebrain_methods_empirical_completeness.png",
                "BeeBrain empirical completeness and anatomy mapping",
            ),
            _module_metric_panel(
                report,
                "BeeMind",
                output_dir / "beemind_methods_policy_landscape.png",
                "BeeMind policy landscape diagnostics",
            ),
            _module_metric_panel(
                report,
                "BeeSwarm",
                output_dir / "beeswarm_methods_contact_recruitment.png",
                "BeeSwarm contact and recruitment diagnostics",
            ),
            _niche_comb_thermal(records, report, output_dir / "beeniche_methods_comb_thermal.png"),
            _manuscript_evidence_index(
                report, output_dir / "methods_manuscript_evidence_index.png"
            ),
        ]
    for path in paths:
        _validate_nonblank_image(path)

    def _plot_data(path: Path) -> dict[str, object]:
        return methods_plot_data(path, report=report, records=records)

    def _sidecar(path: Path) -> dict[str, object]:
        narrative = figure_narrative_for_path(path)
        return {
            "title": narrative.title if narrative is not None else _plot_data(path)["title"],
            "backend": "Matplotlib/pandas",
            "fidelity": _methods_figure_fidelity(path.name),
            "source_data": "MethodsAnalysisReport, simulation records, and manuscript evidence links",
            "validation_status": "nonblank image, quality sidecar, and plot data passed",
            "regeneration_command": "uv run python scripts/run_methods_analysis.py",
        }

    finalize_static_figures(
        paths, plot_data_for=_plot_data, sidecar_for=_sidecar, project_root=project_root
    )
    return paths


def _methods_figure_fidelity(filename: str) -> str:
    """Classify methods figures by evidence tier."""

    if "beebody" in filename:
        return (
            "scripted-pose FlyBody render diagnostics plus reduced telemetry; not forward dynamics"
        )
    if "beebrain" in filename:
        return "empirical completeness summary projected into reduced BeeBrain contracts"
    if "beeswarm" in filename:
        return "scripted-pose scene contact/recruitment diagnostic with reduced-kernel context"
    if "dashboard" in filename or "evidence_index" in filename:
        return "methods provenance diagnostic"
    return "reduced deterministic kernel diagnostic"


def write_interactive_methods_dashboard(
    report: MethodsAnalysisReport,
    output_dir: Path,
) -> list[Path]:
    """Write optional Plotly HTML methods-analysis dashboards."""

    import plotly.express as px
    import plotly.graph_objects as go

    output_dir.mkdir(parents=True, exist_ok=True)
    scorecard_rows = [
        {
            "module": panel.module,
            "validation_fraction": panel.validation_panel.validation_fraction,
            "visual_artifacts": panel.visualization_panel.artifact_count,
            "fidelity_level": panel.fidelity_level,
        }
        for panel in report.module_panels
    ]
    scorecard_path = output_dir / "methods_dashboard.html"
    fig = px.scatter(
        pd.DataFrame(scorecard_rows),
        x="visual_artifacts",
        y="validation_fraction",
        size="visual_artifacts",
        color="fidelity_level",
        hover_name="module",
        range_y=(0, 1.05),
        title="BeeStack methods: configured self-tests and visualization coverage",
        labels={"validation_fraction": "Configured self-test fraction"},
    )
    write_stable_plotly_html(fig, scorecard_path)

    metric_rows = []
    for panel in report.module_panels:
        for metric, value in panel.quantitative_metrics.items():
            metric_rows.append({"module": panel.module, "metric": metric, "value": value})
    metrics_path = output_dir / "methods_module_metrics.html"
    frame = pd.DataFrame(metric_rows)
    fig = go.Figure(
        data=[
            go.Table(
                header={"values": ["Module", "Metric", "Value (native metric units)"]},
                cells={
                    "values": [
                        frame["module"],
                        frame["metric"],
                        ["N/A" if pd.isna(value) else value for value in frame["value"]],
                    ]
                },
                columnwidth=[1, 3, 2],
            )
        ]
    )
    fig.update_layout(
        title="BeeStack module metrics: unlike units are not compared on one axis",
        height=max(500, 26 * len(frame) + 140),
    )
    write_stable_plotly_html(fig, metrics_path)
    return [scorecard_path, metrics_path]


def _repo_methods_dashboard(report: MethodsAnalysisReport, path: Path) -> Path:
    rows = [
        [
            panel.module,
            f"{panel.validation_panel.validation_fraction:.2f}",
            str(len(panel.quantitative_metrics)),
            str(panel.visualization_panel.artifact_count),
            str(len(panel.manuscript_evidence)),
            str(len(panel.known_gaps)),
        ]
        for panel in report.module_panels
    ]
    fig, ax = plt.subplots(figsize=(10.8, max(4.2, 0.48 * len(rows) + 1.8)))
    ax.axis("off")
    ax.set_title("Methods inventory in native units", loc="left", pad=18)
    table = ax.table(
        cellText=rows,
        colLabels=[
            "Module",
            "Self-test\nfraction",
            "Metrics\n(count)",
            "Artifacts\n(count)",
            "Evidence links\n(count)",
            "Known gaps\n(count)",
        ],
        colWidths=[0.19, 0.17, 0.14, 0.16, 0.18, 0.16],
        cellLoc="center",
        bbox=(0, 0.08, 1, 0.84),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    add_figure_note(
        fig,
        "Counts describe report inventory. Self-tests use configured bands, not biological validation; no normalized composite score.",
        y=0.025,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.98))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _methods_dashboard_detail(report: MethodsAnalysisReport, path: Path) -> Path:
    rows = [
        [
            panel.module,
            f"{panel.validation_panel.validation_fraction:.2f}",
            str(panel.visualization_panel.artifact_count),
            str(len(panel.manuscript_evidence)),
            str(len(panel.known_gaps)),
            wrap_label(panel.interpretation, width=58),
        ]
        for panel in report.module_panels
    ]
    row_lines = [2, *(max(len(cell.splitlines()) for cell in row) + 1 for row in rows)]
    fig, ax = plt.subplots(figsize=(12.4, max(5, 0.22 * sum(row_lines) + 1.5)))
    ax.axis("off")
    ax.set_title("Methods detail: module evidence and explicit boundaries", loc="left", pad=16)
    table = ax.table(
        cellText=rows,
        colLabels=["Module", "Self-test\nfraction", "Artifacts", "Evidence", "Gaps", "Boundary"],
        colWidths=[0.11, 0.11, 0.10, 0.10, 0.07, 0.51],
        cellLoc="left",
        bbox=(0, 0.04, 1, 0.88),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    for (row_index, _), cell in table.get_celld().items():
        cell.set_height(row_lines[row_index] / sum(row_lines))
    add_figure_note(
        fig,
        "Full report interpretation is shown; self-tests and source counts do not establish biological validity.",
        y=0.018,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.98))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _body_telemetry(
    records: tuple[dict[str, Any], ...],
    report: MethodsAnalysisReport,
    path: Path,
) -> Path:
    steps = _nullable_series(records, "step_index", default=range(len(records)))
    speed = _nullable_series(records, "body_speed_m_s")
    wing_power = _nullable_series(records, "wing_power_mw")
    energy = _nullable_series(records, "energy_j")
    body_panel = _panel(report, "BeeBody")
    metrics = body_panel.quantitative_metrics
    fig, axes = plt.subplots(2, 2, figsize=(10, 6.4))
    axes[0, 0].plot(steps, speed, color=module_color("BeeBody"), marker="o")
    apply_panel_style(axes[0, 0], title="COM speed witness", ylabel="m/s", grid_axis="both")
    axes[0, 1].plot(steps, wing_power, color=PALETTE[0], marker="s")
    apply_panel_style(axes[0, 1], title="Wingbeat power witness", ylabel="mW", grid_axis="both")
    axes[1, 0].plot(steps, energy, color=module_color("BeeBrain"), marker="^")
    apply_panel_style(axes[1, 0], title="Energy budget", ylabel="J", grid_axis="both")
    labels = ("bee_visual_score", "bee_silhouette_score", "wingbeat_frequency_hz")
    axes[1, 1].axis("off")
    table = axes[1, 1].table(
        cellText=[
            [
                wrap_label(label.replace("_", " "), width=24),
                "Unavailable" if metrics.get(label) is None else f"{metrics[label]:.3g}",
                "Hz" if label.endswith("_hz") else "score",
            ]
            for label in labels
        ],
        colLabels=["Render /\nconfiguration cue", "Value", "Unit"],
        colWidths=[0.62, 0.23, 0.15],
        cellLoc="left",
        bbox=(0, 0.08, 1, 0.75),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    axes[1, 1].set_title("Morphology and wingbeat cues")
    for axis in (axes[0, 0], axes[0, 1], axes[1, 0]):
        axis.set_xlabel("Control step")
    for label, axis in zip(("A", "B", "C", "D"), axes.ravel(), strict=True):
        add_panel_label(axis, label)
    fig.suptitle("BeeBody methods telemetry and morphology diagnostics", y=0.995)
    add_figure_note(
        fig,
        "Reduced telemetry and scripted-pose render cues; not forward-dynamics or biological validation.",
        y=0.012,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _module_metric_panel(
    report: MethodsAnalysisReport,
    module: str,
    path: Path,
    title: str,
) -> Path:
    panel = _panel(report, module)
    items = sorted(panel.quantitative_metrics.items())
    row_lines = max((len(wrap_label(name, width=28).splitlines()) for name, _ in items), default=1)
    fig = plt.figure(figsize=(11.8, max(6.4, 0.24 * (len(items) + 1) * row_lines + 1.2)))
    grid = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0])
    ax = fig.add_subplot(grid[0, 0])
    ax_context = fig.add_subplot(grid[0, 1])
    ax.axis("off")
    table = ax.table(
        cellText=[
            [wrap_label(name, width=28), "N/A" if value is None else f"{value:.3g}"]
            for name, value in items
        ],
        colLabels=["Metric (native units)", "Value"],
        colWidths=[0.72, 0.28],
        cellLoc="left",
        bbox=(0, 0.03, 1, 0.9),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    ax.set_title(wrap_label(title, width=48), fontsize=11)
    add_panel_label(ax, "A")
    ax_context.axis("off")
    evidence = panel.manuscript_evidence[0]
    context_lines = (
        f"Configured self-test fraction\n{panel.validation_panel.validation_fraction:.2f}",
        f"Linked visual artifacts\n{panel.visualization_panel.artifact_count}",
        f"Claim tier\n{evidence.claim_tier.replace('_', ' ')}",
        f"Availability\n{evidence.availability_status}",
        "Conservative boundary\n" + panel.interpretation,
    )
    context = [wrap_label(text, width=42) for text in context_lines]
    context_table = ax_context.table(
        cellText=[[text] for text in context],
        colWidths=[1.0],
        cellLoc="left",
        bbox=(0, 0.03, 1, 0.9),
    )
    context_table.auto_set_font_size(False)
    context_table.set_fontsize(8.5)
    context_heights = [len(text.splitlines()) + 1 for text in context]
    for (row_index, _), cell in context_table.get_celld().items():
        cell.set_height(context_heights[row_index] / sum(context_heights))
    add_panel_label(ax_context, "B")
    fig.suptitle(f"{module}: methods evidence, self-tests, and claim boundary", y=0.975)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _niche_comb_thermal(
    records: tuple[dict[str, Any], ...],
    report: MethodsAnalysisReport,
    path: Path,
) -> Path:
    steps = _nullable_series(records, "step_index", default=range(len(records)))
    comb = _nullable_series(records, "comb_fraction")
    temp_error = _nullable_series(records, "brood_temperature_error_c")
    panel = _panel(report, "BeeNiche")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.7))
    axes[0].plot(steps, comb, marker="s", color=module_color("BeeNiche"))
    apply_panel_style(
        axes[0],
        title="Comb occupancy trajectory",
        xlabel="Control step",
        ylabel="Fraction",
        grid_axis="both",
    )
    axes[1].plot(steps, temp_error, marker="o", color=PALETTE[6])
    apply_panel_style(
        axes[1],
        title="Brood thermal error",
        xlabel="Control step",
        ylabel="C",
        grid_axis="both",
    )
    for label, axis in zip(("A", "B"), axes, strict=True):
        add_panel_label(axis, label)
    fig.suptitle(
        f"BeeNiche reduced diagnostics; configured self-test fraction {panel.validation_panel.validation_fraction:.2f}",
        y=0.98,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _manuscript_evidence_index(report: MethodsAnalysisReport, path: Path) -> Path:
    rows = []
    for panel in report.module_panels:
        rows.append(
            {
                "module": panel.module,
                "evidence_links": len(panel.manuscript_evidence),
                "visual_artifacts": panel.visualization_panel.artifact_count,
                "validation_fraction": panel.validation_panel.validation_fraction,
            }
        )
    frame = pd.DataFrame(rows)
    x = np.arange(len(frame))
    fig, (ax, ax_tests) = plt.subplots(
        1, 2, figsize=(11.2, 4.8), gridspec_kw={"width_ratios": [1.3, 1]}
    )
    ax.bar(
        x - 0.2,
        frame["evidence_links"],
        width=0.4,
        label="Evidence links",
        color=module_color("BeeBrain"),
    )
    ax.bar(
        x + 0.2,
        frame["visual_artifacts"],
        width=0.4,
        label="Visual artifacts",
        color=module_color("BeeBody"),
    )
    ax.set_xticks(x, frame["module"], rotation=20, ha="right")
    ax.set_ylabel("Count")
    ax.set_title("Manuscript evidence inventory")
    apply_panel_style(ax, grid_axis="y")
    ax.legend(loc="upper left", fontsize=8)
    bars = ax_tests.barh(frame["module"], frame["validation_fraction"], color=PALETTE[5])
    for bar, value in zip(bars, frame["validation_fraction"], strict=True):
        ax_tests.text(
            1.02,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f}",
            transform=ax_tests.get_yaxis_transform(),
            va="center",
            color="#334155",
        )
    ax_tests.set_xlim(0, 1.05)
    apply_panel_style(
        ax_tests,
        title="Configured self-tests",
        xlabel="Fraction (not biological validation)",
        grid_axis="x",
    )
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _panel(report: MethodsAnalysisReport, module: str):
    return next(panel for panel in report.module_panels if panel.module == module)


def _validate_nonblank_image(path: Path) -> None:
    assert_nonblank_quality(path)
