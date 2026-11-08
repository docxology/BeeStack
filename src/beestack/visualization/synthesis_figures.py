"""Cross-stack synthesis figures."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .figure_metadata import assert_nonblank_quality, write_figure_artifacts
from .figure_plot_specs import synthesis_plot_data
from .figure_registry import figure_narrative_for_path
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
    from ..research import StackSynthesisReview


def generate_stack_synthesis_figures(
    review: StackSynthesisReview,
    output_dir: Path,
    *,
    project_root: Path | None = None,
) -> list[Path]:
    """Generate cross-stack synthesis figures."""

    output_dir.mkdir(parents=True, exist_ok=True)
    with style_context():
        paths = [
            _stack_synthesis_dashboard(review, output_dir / "stack_synthesis_dashboard.png"),
            _stack_synthesis_findings_detail(
                review, output_dir / "stack_synthesis_findings_detail.png"
            ),
        ]
    for path in paths:
        _validate_nonblank_image(path)
        narrative = figure_narrative_for_path(path)
        plot_data = synthesis_plot_data(path, review=review)
        write_figure_artifacts(
            path,
            plot_data,
            title=narrative.title if narrative is not None else plot_data["title"],
            backend="Matplotlib/pandas synthesis dashboard",
            fidelity="cross-stack synthesis diagnostic, not biological validation",
            source_data="output/reports/stack_synthesis_review.json",
            validation_status="nonblank synthesis diagnostic with plot data",
            regeneration_command="uv run python scripts/run_research_suite.py",
            project_root=project_root,
        )
    return paths


def _stack_synthesis_dashboard(review: StackSynthesisReview, path: Path) -> Path:
    frame = pd.DataFrame([panel.as_dict() for panel in review.module_panels])
    finding_lines = [wrap_label(finding, width=58) for finding in review.prioritized_findings]
    finding_line_count = sum(len(text.splitlines()) + 1 for text in finding_lines)
    fig = plt.figure(figsize=(13.2, max(9, 0.42 * finding_line_count + 3)))
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.1])
    ax_readiness = fig.add_subplot(grid[0, 0])
    ax_artifacts = fig.add_subplot(grid[0, 1])
    ax_stats = fig.add_subplot(grid[1, 0])
    ax_findings = fig.add_subplot(grid[1, 1])

    x = np.arange(len(frame))
    colors = [module_color(module) for module in frame["module"]]
    ax_readiness.bar(
        x - 0.18,
        frame["validation_fraction"],
        width=0.36,
        label="Configured self-tests",
        color=colors,
        alpha=0.86,
    )
    ax_readiness.bar(
        x + 0.18,
        frame["readiness_score"],
        width=0.36,
        label="Heuristic readiness",
        color=PALETTE[5],
        alpha=0.72,
    )
    ax_readiness.set_xticks(x, frame["module"], rotation=25, ha="right")
    ax_readiness.set_ylim(0, 1.05)
    ax_readiness.set_ylabel("Self-test fraction / readiness score")
    ax_readiness.set_title("Configured checks and report readiness")
    ax_readiness.legend(fontsize=8, loc="upper left", bbox_to_anchor=(0, 1.03))
    ax_readiness.set_ylim(0, 1.22)
    apply_panel_style(ax_readiness, grid_axis="y")

    ax_artifacts.axis("off")
    ax_artifacts.set_title("Module report inventory (counts)", loc="left")
    table = ax_artifacts.table(
        cellText=[
            [row.module, str(row.artifact_count), str(row.known_gap_count), str(row.metric_count)]
            for row in frame.itertuples()
        ],
        colLabels=["Module", "Artifacts", "Known gaps", "Metrics"],
        colWidths=[0.28, 0.24, 0.24, 0.24],
        cellLoc="center",
        bbox=(0, 0.05, 1, 0.86),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9.5)

    stat_names = [
        "simulation_thermal_error_improvement_c",
        "module_artifact_coverage_fraction",
        "empirical_parseable_fraction",
        "signposting_fraction",
        "scholarship_reference_count",
    ]
    stat_labels = [
        "Reduced thermal-error improvement",
        "Module artifact coverage",
        "Empirical source parseability",
        "Documentation signposting",
        "Scholarship references",
    ]
    stat_units = ["°C", "fraction", "fraction", "fraction", "count"]
    ax_stats.axis("off")
    ax_stats.set_title("Cross-stack statistics (native units)", loc="left")
    table = ax_stats.table(
        cellText=[
            [
                wrap_label(label, width=32),
                "Unavailable"
                if review.statistics[name] is None
                else f"{review.statistics[name]:.3g}",
                unit,
            ]
            for name, label, unit in zip(stat_names, stat_labels, stat_units, strict=True)
        ],
        colLabels=["Statistic", "Value", "Unit"],
        colWidths=[0.63, 0.17, 0.20],
        cellLoc="left",
        bbox=(0, 0.05, 1, 0.87),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)

    ax_findings.axis("off")
    y = 0.94
    for index, text in enumerate(finding_lines, start=1):
        ax_findings.text(
            0.0,
            y,
            f"{index}. {text}",
            transform=ax_findings.transAxes,
            va="top",
            fontsize=9,
            color="#334155",
        )
        y -= 0.90 * (len(text.splitlines()) + 1) / max(1, finding_line_count)
    ax_findings.set_title("Prioritized findings", loc="left")
    for label, axis in zip(
        ("A", "B", "C", "D"),
        (ax_readiness, ax_artifacts, ax_stats, ax_findings),
        strict=True,
    ):
        add_panel_label(axis, label)

    fig.suptitle("BeeStack cross-stack synthesis dashboard", y=0.99)
    add_figure_note(
        fig,
        "Configured self-tests and heuristic readiness describe the reduced stack and its source inventory, not biological validation. Statistics retain native values and signs.",
        y=0.012,
    )
    fig.tight_layout(rect=(0, 0.035, 1, 0.97))
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _stack_synthesis_findings_detail(review: StackSynthesisReview, path: Path) -> Path:
    frame = pd.DataFrame([panel.as_dict() for panel in review.module_panels])
    findings = [wrap_label(finding, width=62) for finding in review.prioritized_findings]
    line_count = sum(len(text.splitlines()) + 1 for text in findings)
    fig = plt.figure(figsize=(12.8, max(6.5, 0.25 * line_count + 1.8)))
    grid = fig.add_gridspec(1, 2, width_ratios=[0.9, 1.2])
    ax_modules = fig.add_subplot(grid[0, 0])
    ax_findings = fig.add_subplot(grid[0, 1])
    ax_modules.axis("off")
    ax_modules.set_title("Heuristic readiness and report gaps", loc="left")
    table = ax_modules.table(
        cellText=[
            [row.module, f"{row.readiness_score:.2f}", str(row.known_gap_count)]
            for row in frame.itertuples()
        ],
        colLabels=["Module", "Readiness score", "Known gaps"],
        colWidths=[0.34, 0.38, 0.28],
        cellLoc="left",
        bbox=(0, 0.10, 1, 0.78),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9.5)
    add_panel_label(ax_modules, "A")
    ax_findings.axis("off")
    ax_findings.set_title("Prioritized findings", loc="left")
    y = 0.94
    for index, text in enumerate(findings, start=1):
        ax_findings.text(
            0.02,
            y,
            f"{index}. {text}",
            transform=ax_findings.transAxes,
            va="top",
            fontsize=9,
            color="#334155",
        )
        y -= 0.90 * (len(text.splitlines()) + 1) / max(1, line_count)
    add_panel_label(ax_findings, "B")
    fig.suptitle("BeeStack synthesis detail: readiness, gaps, and findings", y=0.98)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _validate_nonblank_image(path: Path) -> None:
    assert_nonblank_quality(path)
