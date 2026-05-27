"""Cross-stack synthesis figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..research import StackSynthesisReview
from .figure_metadata import assert_nonblank_quality, write_figure_artifacts
from .figure_plot_specs import synthesis_plot_data
from .style import (
    PALETTE,
    add_panel_label,
    apply_panel_style,
    bounded_text,
    module_color,
    status_color,
    style_context,
    wrap_label,
)


def generate_stack_synthesis_figures(
    review: StackSynthesisReview,
    output_dir: Path,
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
        write_figure_artifacts(
            path,
            synthesis_plot_data(path, review=review),
            title=path.stem.replace("_", " ").title(),
            backend="Matplotlib/pandas synthesis dashboard",
            fidelity="cross-stack synthesis diagnostic, not biological validation",
            source_data="output/reports/stack_synthesis_review.json",
            validation_status="nonblank synthesis diagnostic with plot data",
            regeneration_command="uv run python scripts/run_research_suite.py",
        )
    return paths


def _stack_synthesis_dashboard(review: StackSynthesisReview, path: Path) -> Path:
    frame = pd.DataFrame([panel.as_dict() for panel in review.module_panels])
    fig = plt.figure(figsize=(12, 8))
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
        label="validation",
        color=colors,
        alpha=0.86,
    )
    ax_readiness.bar(
        x + 0.18,
        frame["readiness_score"],
        width=0.36,
        label="readiness",
        color=PALETTE[5],
        alpha=0.72,
    )
    ax_readiness.set_xticks(x, frame["module"], rotation=25, ha="right")
    ax_readiness.set_ylim(0, 1.05)
    ax_readiness.set_ylabel("Fraction")
    ax_readiness.set_title("Module validation and synthesized readiness")
    ax_readiness.legend(fontsize=8)
    ax_readiness.axhline(0.80, color=status_color("warning"), lw=0.9, ls="--", alpha=0.75)
    ax_readiness.text(
        0.02,
        0.82,
        "readiness target",
        transform=ax_readiness.get_yaxis_transform(),
        ha="left",
        va="bottom",
        fontsize=7.5,
        color="#334155",
    )
    apply_panel_style(ax_readiness, grid_axis="y")

    points = ax_artifacts.scatter(
        frame["artifact_count"],
        frame["known_gap_count"],
        s=(frame["metric_count"] + 1) * 34,
        c=frame["readiness_score"],
        cmap="viridis",
        vmin=0,
        vmax=1,
        edgecolor="#1f2937",
    )
    label_offsets = {
        "BeeBody": (0.15, 0.08),
        "BeeBrain": (-0.65, -0.12),
        "BeeMind": (0.10, 0.08),
        "BeeSwarm": (-0.60, 0.08),
        "BeeNiche": (0.10, 0.08),
    }
    for row in frame.itertuples():
        dx, dy = label_offsets.get(row.module, (0.1, 0.05))
        ax_artifacts.text(
            row.artifact_count + dx,
            row.known_gap_count + dy,
            row.module,
            fontsize=8,
            bbox={"boxstyle": "round,pad=0.15", "facecolor": "white", "alpha": 0.65, "lw": 0},
        )
    ax_artifacts.set_xlim(
        max(0, float(frame["artifact_count"].min()) - 1.0),
        float(frame["artifact_count"].max()) + 1.2,
    )
    ax_artifacts.set_ylim(
        max(0, float(frame["known_gap_count"].min()) - 0.25),
        float(frame["known_gap_count"].max()) + 0.45,
    )
    ax_artifacts.set_xlabel("Artifact count")
    ax_artifacts.set_ylabel("Known gap count")
    ax_artifacts.set_title("Artifacts versus explicit gaps")
    fig.colorbar(points, ax=ax_artifacts, label="readiness score", fraction=0.046, pad=0.02)
    apply_panel_style(ax_artifacts, grid_axis="both")

    stat_names = [
        "simulation_thermal_error_improvement_c",
        "module_artifact_coverage_fraction",
        "empirical_parseable_fraction",
        "signposting_fraction",
        "scholarship_reference_count",
    ]
    raw_values = [review.statistics[name] for name in stat_names]
    stat_values = [
        min(1.0, review.statistics["simulation_thermal_error_improvement_c"] / 3.0),
        review.statistics["module_artifact_coverage_fraction"],
        review.statistics["empirical_parseable_fraction"],
        review.statistics["signposting_fraction"],
        min(1.0, review.statistics["scholarship_reference_count"] / 7.0),
    ]
    labels = [
        wrap_label("Thermal improvement C", width=13, max_lines=2),
        wrap_label("Artifact coverage", width=13, max_lines=2),
        wrap_label("Brain parseable", width=13, max_lines=2),
        "Signposting",
        wrap_label("Scholarship refs", width=13, max_lines=2),
    ]
    bars = ax_stats.bar(
        labels,
        stat_values,
        color=[
            module_color("BeeNiche"),
            module_color("BeeBrain"),
            module_color("BeeMind"),
            module_color("BeeBody"),
            PALETTE[5],
        ],
    )
    for bar, raw in zip(bars, raw_values, strict=True):
        ax_stats.text(
            bar.get_x() + bar.get_width() / 2,
            min(1.04, bar.get_height() + 0.03),
            f"{raw:.2g}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    ax_stats.set_ylim(0, 1.12)
    ax_stats.set_ylabel("Normalized gate score")
    ax_stats.set_title("Cross-stack statistical gates")
    apply_panel_style(ax_stats, grid_axis="y")

    ax_findings.axis("off")
    finding_text = "\n\n".join(
        f"- {wrap_label(finding, width=58, max_lines=3)}"
        for finding in review.prioritized_findings
    )
    bounded_text(
        ax_findings,
        0.0,
        0.96,
        finding_text,
        width=68,
        max_lines=12,
        fontsize=8.6,
        facecolor="#F8FAFC",
    )
    ax_findings.set_title("Prioritized findings", loc="left")
    for label, axis in zip(
        ("A", "B", "C", "D"),
        (ax_readiness, ax_artifacts, ax_stats, ax_findings),
        strict=True,
    ):
        add_panel_label(axis, label)

    fig.suptitle("BeeStack cross-stack synthesis dashboard", y=0.99)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _stack_synthesis_findings_detail(review: StackSynthesisReview, path: Path) -> Path:
    frame = pd.DataFrame([panel.as_dict() for panel in review.module_panels])
    fig = plt.figure(figsize=(11.8, 6.5))
    grid = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.0])
    ax_modules = fig.add_subplot(grid[0, 0])
    ax_findings = fig.add_subplot(grid[0, 1])
    y = np.arange(len(frame))
    bars = ax_modules.barh(
        y,
        frame["readiness_score"],
        color=[module_color(module) for module in frame["module"]],
        alpha=0.88,
    )
    ax_modules.set_yticks(y, frame["module"])
    ax_modules.set_xlim(0, 1.05)
    ax_modules.axvline(0.80, color=status_color("warning"), lw=1.0, ls="--")
    for bar, row in zip(bars, frame.itertuples(), strict=True):
        ax_modules.text(
            min(1.02, float(row.readiness_score) + 0.025),
            bar.get_y() + bar.get_height() / 2,
            f"ready {row.readiness_score:.2f}; gaps {row.known_gap_count}",
            va="center",
            ha="left",
            fontsize=8,
            color="#334155",
        )
    apply_panel_style(
        ax_modules,
        title="Module readiness with explicit gaps",
        xlabel="Synthesized readiness score",
        grid_axis="x",
    )
    add_panel_label(ax_modules, "A")
    ax_findings.axis("off")
    ax_findings.set_title("Prioritized findings", loc="left")
    for index, finding in enumerate(review.prioritized_findings[:5]):
        bounded_text(
            ax_findings,
            0.02,
            0.92 - index * 0.17,
            finding,
            width=58,
            max_lines=3,
            fontsize=8.2,
            facecolor="#F8FAFC",
        )
    add_panel_label(ax_findings, "B")
    fig.suptitle("BeeStack synthesis detail: readiness, gaps, and findings", y=0.98)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _validate_nonblank_image(path: Path) -> None:
    assert_nonblank_quality(path)
