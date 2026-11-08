"""Research-suite figures and interactive outputs."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

from .figure_metadata import assert_nonblank_quality
from .figure_output import finalize_static_figures, write_stable_plotly_html
from .figure_plot_specs import research_evidence_rows, research_inventory_rows, research_plot_data
from .figure_registry import figure_narrative_for_path
from .style import (
    add_figure_note,
    apply_panel_style,
    module_color,
    style_context,
    wrap_label,
)

if TYPE_CHECKING:
    from ..research import ResearchSuiteReport


def generate_research_figures(
    report: ResearchSuiteReport,
    output_dir: Path,
    *,
    project_root: Path | None = None,
) -> list[Path]:
    """Generate science-first research report figures."""

    output_dir.mkdir(parents=True, exist_ok=True)
    with style_context():
        paths = [
            _module_inventory_table(report, output_dir / "research_module_scorecard_heatmap.png"),
            _validation_bars(report, output_dir / "research_validation_scorecard.png"),
            _sensitivity_sweeps(report, output_dir / "research_sensitivity_sweeps.png"),
            _evidence_inventory_table(
                report, output_dir / "research_fidelity_evidence_network.png"
            ),
            _evidence_detail(report, output_dir / "research_evidence_detail.png"),
            _visualization_inventory(report, output_dir / "research_visualization_inventory.png"),
            _empirical_completeness(report, output_dir / "research_empirical_completeness.png"),
            _module_metric_table(report, "BeeBody", output_dir / "beebody_method_diagnostics.png"),
            _module_metric_table(
                report, "BeeBrain", output_dir / "beebrain_empirical_evidence_map.png"
            ),
            _module_metric_table(report, "BeeMind", output_dir / "beemind_policy_sensitivity.png"),
            _module_metric_table(
                report, "BeeSwarm", output_dir / "beeswarm_contact_recruitment_scorecard.png"
            ),
            _module_metric_table(
                report, "BeeNiche", output_dir / "beeniche_thermal_comb_scorecard.png"
            ),
        ]
    for path in paths:
        _validate_nonblank_image(path)

    def _plot_data(path: Path) -> dict[str, object]:
        return research_plot_data(path, report=report)

    def _sidecar(path: Path) -> dict[str, object]:
        narrative = figure_narrative_for_path(path)
        return {
            "title": narrative.title if narrative is not None else _plot_data(path)["title"],
            "backend": "Matplotlib/pandas",
            "fidelity": _research_figure_fidelity(path.name),
            "source_data": "ResearchSuiteReport scorecards, evidence records, sweeps, and visual inventory",
            "validation_status": "nonblank image, quality sidecar, and plot data passed",
            "regeneration_command": "uv run python scripts/run_research_suite.py",
        }

    finalize_static_figures(
        paths, plot_data_for=_plot_data, sidecar_for=_sidecar, project_root=project_root
    )
    return paths


def _research_figure_fidelity(filename: str) -> str:
    """Classify research-suite figures by evidence tier."""

    if "empirical" in filename or "beebrain" in filename:
        return "empirical source inventory / parseability diagnostic; not biological validation"
    if "beebody" in filename:
        return (
            "scripted-pose FlyBody render diagnostics plus reduced telemetry; not forward dynamics"
        )
    if any(token in filename for token in ("network", "inventory", "scorecard", "evidence")):
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
        title="BeeStack research configured self-test scorecards (not biological validation)",
        labels={"validation_fraction": "Configured self-test fraction"},
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
        facet_row="output_name",
        title="Reduced-kernel sensitivity: independent native-unit axes; missing output has no points",
    )
    fig.update_xaxes(matches=None, showticklabels=True)
    fig.update_yaxes(matches=None, showticklabels=True)
    fig.update_layout(height=1100, showlegend=False)
    write_stable_plotly_html(fig, sweep_path)
    return [scorecard_path, sweep_path]


def _module_inventory_table(report: ResearchSuiteReport, path: Path) -> Path:
    rows = [
        [
            row["module"],
            f"{row['validation_fraction']:.2f}",
            str(row["metric_count"]),
            str(row["evidence_count"]),
            str(row["known_gap_count"]),
            str(row["visual_artifacts"]),
        ]
        for row in research_inventory_rows(report)
    ]
    fig, ax = plt.subplots(figsize=(10.8, max(4.2, 0.48 * len(rows) + 1.8)))
    ax.axis("off")
    ax.set_title("Research inventory in native units", loc="left", pad=18)
    table = ax.table(
        cellText=rows,
        colLabels=[
            "Module",
            "Self-test\nfraction",
            "Metrics\n(count)",
            "Evidence\n(count)",
            "Known gaps\n(count)",
            "Artifacts\n(count)",
        ],
        colWidths=[0.19, 0.17, 0.14, 0.16, 0.18, 0.16],
        cellLoc="center",
        bbox=(0, 0.08, 1, 0.84),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    add_figure_note(
        fig,
        "Counts are report inventory; configured self-tests are not biological validation. Unlike metrics are not combined into a score.",
        y=0.025,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.98))
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


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
    bars = ax.bar(
        frame["module"],
        frame["validation_fraction"],
        color=[module_color(module) for module in frame["module"]],
    )
    ax.bar_label(bars, fmt="%.2f", padding=3)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Configured self-test fraction")
    ax.set_title("Configured self-tests (not biological validation)")
    apply_panel_style(ax, grid_axis="y")
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _sensitivity_sweeps(report: ResearchSuiteReport, path: Path) -> Path:
    output_names = tuple(
        dict.fromkeys(name for sweep in report.sensitivity_sweeps for name in sweep.outputs)
    )
    fig, axes = plt.subplots(
        len(output_names),
        len(report.sensitivity_sweeps),
        figsize=(max(10, 3.6 * len(report.sensitivity_sweeps)), 2.6 * len(output_names)),
        squeeze=False,
    )
    for column, sweep in enumerate(report.sensitivity_sweeps):
        for row, output_name in enumerate(output_names):
            axis = axes[row, column]
            values = sweep.outputs.get(output_name)
            if values is not None and any(value is not None for value in values):
                axis.plot(sweep.values, values, marker="o")
            else:
                axis.text(0.5, 0.5, "Unavailable", ha="center", transform=axis.transAxes)
            if row == 0:
                axis.set_title(wrap_label(sweep.parameter, width=24), fontsize=9)
            if column == 0:
                axis.set_ylabel(wrap_label(output_name.replace("_", " "), width=22), fontsize=8)
            axis.grid(alpha=0.22)
    fig.suptitle("Reduced-kernel sensitivity sweeps", y=0.995)
    add_figure_note(
        fig,
        "Independent native-unit axes; unavailable outputs are not zero. Not empirical validation.",
        y=0.012,
    )
    fig.tight_layout(rect=(0, 0.035, 1, 0.97))
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _evidence_inventory_table(report: ResearchSuiteReport, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10.4, 5.5))
    ax.axis("off")
    ax.set_title("Evidence inventory overview", loc="left", pad=16)
    table = ax.table(
        cellText=[
            [
                card.module,
                str(len(card.evidence)),
                str(len(card.known_gaps)),
                wrap_label(card.fidelity_level, width=46),
            ]
            for card in report.module_scorecards
        ],
        colLabels=["Module", "Evidence rows", "Known gaps", "Reported fidelity"],
        colWidths=[0.17, 0.15, 0.15, 0.53],
        cellLoc="left",
        bbox=(0, 0.08, 1, 0.84),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    add_figure_note(
        fig,
        f"{len(report.empirical_evidence)} empirical source records are detailed in the companion. Counts are provenance, not measured biological connectivity or validation.",
        y=0.02,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.98))
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _evidence_detail(report: ResearchSuiteReport, path: Path) -> Path:
    rows = research_evidence_rows(report)
    headers = ("Module", "Kind", "Evidence item", "Status", "Boundary / target")
    keys = ("module", "kind", "item", "status", "boundary")
    widths = (12, 10, 38, 22, 44)
    cells = [
        [wrap_label(row[key], width=width) for key, width in zip(keys, widths, strict=True)]
        for row in rows
    ]
    row_lines = [2, *(max(len(cell.splitlines()) for cell in row) + 1 for row in cells)]
    fig, ax = plt.subplots(figsize=(13.2, max(5.2, 0.22 * sum(row_lines) + 1.5)))
    ax.axis("off")
    ax.set_title("Research evidence detail: report sources and explicit gaps", loc="left", pad=16)
    table = ax.table(
        cellText=cells,
        colLabels=headers,
        colWidths=[0.10, 0.09, 0.30, 0.17, 0.34],
        cellLoc="left",
        bbox=(0, 0.03, 1, 0.92),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    for (row_index, _), cell in table.get_celld().items():
        cell.set_height(row_lines[row_index] / sum(row_lines))
    add_figure_note(
        fig,
        "All current-report rows are shown. Aggregate availability is not a standalone payload inventory or biological validation.",
        y=0.012,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.98))
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _visualization_inventory(report: ResearchSuiteReport, path: Path) -> Path:
    frame = pd.DataFrame([artifact.as_dict() for artifact in report.visualization_artifacts])
    counts = frame.groupby(["artifact_type", "fidelity_level"]).size().reset_index(name="count")
    labels = [
        wrap_label(f"{row.artifact_type}: {row.fidelity_level}", width=64)
        for row in counts.itertuples()
    ]
    line_count = sum(max(1, len(label.splitlines())) for label in labels)
    fig, ax = plt.subplots(figsize=(11.5, max(4.5, 0.30 * line_count + 1.4)))
    bars = ax.barh(labels[::-1], counts["count"].to_numpy()[::-1], color=module_color("BeeBody"))
    ax.bar_label(bars, padding=4, fmt="%g")
    ax.margins(x=0.15)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel("Artifact count (inventory, not validation)")
    ax.set_title("Visualization artifact inventory by reported fidelity")
    apply_panel_style(ax, grid_axis="x")
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _empirical_completeness(report: ResearchSuiteReport, path: Path) -> Path:
    rows = [
        [
            wrap_label(record.dataset_id, width=44),
            f"{record.completeness_fraction:.2f}",
            wrap_label(record.availability_status, width=44),
        ]
        for record in report.empirical_evidence
    ]
    row_lines = max((max(len(cell.splitlines()) for cell in row) for row in rows), default=1)
    fig, ax = plt.subplots(figsize=(11.2, max(4.4, 0.24 * (len(rows) + 1) * row_lines + 1.4)))
    ax.axis("off")
    ax.set_title("Current-aggregate evidence availability (reported state)", loc="left", pad=16)
    table = ax.table(
        cellText=rows,
        colLabels=["Dataset", "Completeness fraction", "Availability status"],
        colWidths=[0.40, 0.20, 0.40],
        cellLoc="left",
        bbox=(0, 0.06, 1, 0.86),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    add_figure_note(
        fig,
        "Fractions describe source availability / parseability. Status comes from the report, not a numeric cutoff; neither is biological validation.",
        y=0.018,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.98))
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _module_metric_table(report: ResearchSuiteReport, module: str, path: Path) -> Path:
    scorecard = next(item for item in report.module_scorecards if item.module == module)
    items = sorted(scorecard.metrics.items())
    row_lines = max((len(wrap_label(name, width=34).splitlines()) for name, _ in items), default=1)
    fig, ax = plt.subplots(figsize=(9.5, max(4.8, 0.25 * (len(items) + 1) * row_lines + 1.3)))
    ax.axis("off")
    table = ax.table(
        cellText=[
            [wrap_label(name, width=34), "Unavailable" if value is None else f"{value:.3g}"]
            for name, value in items
        ],
        colLabels=["Metric (native units)", "Value"],
        colWidths=[0.75, 0.25],
        cellLoc="left",
        bbox=(0, 0.03, 1, 0.9),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    ax.set_title(f"{module} research diagnostics: native-unit metric table")
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _validate_nonblank_image(path: Path) -> None:
    assert_nonblank_quality(path)
