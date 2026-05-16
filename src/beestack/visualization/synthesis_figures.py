"""Cross-stack synthesis figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..research import StackSynthesisReview
from .figure_metadata import assert_nonblank_quality, write_figure_sidecar


def generate_stack_synthesis_figures(
    review: StackSynthesisReview,
    output_dir: Path,
) -> list[Path]:
    """Generate cross-stack synthesis figures."""

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        _stack_synthesis_dashboard(review, output_dir / "stack_synthesis_dashboard.png"),
    ]
    for path in paths:
        _validate_nonblank_image(path)
        write_figure_sidecar(
            path,
            title=path.stem.replace("_", " ").title(),
            backend="Matplotlib/pandas synthesis dashboard",
            fidelity="cross-stack synthesis diagnostic, not biological validation",
            source_data="output/reports/stack_synthesis_review.json",
            validation_status="nonblank synthesis diagnostic",
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
    ax_readiness.bar(x - 0.18, frame["validation_fraction"], width=0.36, label="validation")
    ax_readiness.bar(x + 0.18, frame["readiness_score"], width=0.36, label="readiness")
    ax_readiness.set_xticks(x, frame["module"], rotation=25, ha="right")
    ax_readiness.set_ylim(0, 1.05)
    ax_readiness.set_ylabel("Fraction")
    ax_readiness.set_title("Module validation and synthesized readiness")
    ax_readiness.legend(fontsize=8)
    ax_readiness.grid(axis="y", alpha=0.2)

    ax_artifacts.scatter(
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
    ax_artifacts.grid(alpha=0.2)

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
        "Thermal\nimprovement C",
        "Artifact\ncoverage",
        "Brain\nparseable",
        "Signposting",
        "Scholarship\nrefs",
    ]
    bars = ax_stats.bar(
        labels,
        stat_values,
        color=["#0f766e", "#2563eb", "#7c3aed", "#ca8a04", "#475569"],
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
    ax_stats.grid(axis="y", alpha=0.2)

    ax_findings.axis("off")
    finding_text = "\n\n".join(f"- {finding}" for finding in review.prioritized_findings)
    ax_findings.text(
        0.0,
        1.0,
        finding_text,
        va="top",
        ha="left",
        fontsize=9,
        wrap=True,
        transform=ax_findings.transAxes,
    )
    ax_findings.set_title("Prioritized findings", loc="left")

    fig.suptitle("BeeStack cross-stack synthesis dashboard", y=0.99)
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def _validate_nonblank_image(path: Path) -> None:
    assert_nonblank_quality(path)
