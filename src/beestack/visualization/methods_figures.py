"""Methods-analysis figures and interactive dashboards."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..research import MethodsAnalysisReport
from .figure_metadata import assert_nonblank_quality
from .figure_output import finalize_static_figures
from .figure_plot_specs import methods_plot_data
from .style import (
    PALETTE,
    add_panel_label,
    apply_panel_style,
    bounded_text,
    direct_label_bars,
    format_compact_number,
    module_color,
    style_context,
    wrap_label,
)


def generate_methods_figures(
    report: MethodsAnalysisReport,
    records: tuple[dict[str, Any], ...],
    output_dir: Path,
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
        return {
            "title": path.stem.replace("_", " ").title(),
            "backend": "Matplotlib/pandas",
            "fidelity": _methods_figure_fidelity(path.name),
            "source_data": "MethodsAnalysisReport, simulation records, and manuscript evidence links",
            "validation_status": "nonblank image, quality sidecar, and plot data passed",
            "regeneration_command": "uv run python scripts/run_methods_analysis.py",
        }

    finalize_static_figures(paths, plot_data_for=_plot_data, sidecar_for=_sidecar)
    return paths


def _methods_figure_fidelity(filename: str) -> str:
    """Classify methods figures by evidence tier."""

    if "beebody" in filename:
        return "FlyBody-backed render diagnostics plus reduced telemetry"
    if "beebrain" in filename:
        return "empirical completeness summary projected into reduced BeeBrain contracts"
    if "beeswarm" in filename:
        return "strict scene contact/recruitment diagnostic with reduced-kernel context"
    if "dashboard" in filename or "evidence_index" in filename:
        return "methods provenance diagnostic"
    return "reduced deterministic kernel diagnostic"


def write_interactive_methods_dashboard(
    report: MethodsAnalysisReport,
    output_dir: Path,
) -> list[Path]:
    """Write optional Plotly HTML methods-analysis dashboards."""

    import plotly.express as px

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
        title="BeeStack methods-analysis validation and visualization coverage",
    )
    fig.write_html(scorecard_path, include_plotlyjs="cdn")

    metric_rows = []
    for panel in report.module_panels:
        for metric, value in panel.quantitative_metrics.items():
            metric_rows.append({"module": panel.module, "metric": metric, "value": value})
    metrics_path = output_dir / "methods_module_metrics.html"
    fig = px.bar(
        pd.DataFrame(metric_rows),
        x="metric",
        y="value",
        color="module",
        facet_col="module",
        facet_col_wrap=2,
        title="BeeStack methods-analysis module metrics",
    )
    fig.update_xaxes(tickangle=45)
    fig.write_html(metrics_path, include_plotlyjs="cdn")
    return [scorecard_path, metrics_path]


def _repo_methods_dashboard(report: MethodsAnalysisReport, path: Path) -> Path:
    rows = []
    for panel in report.module_panels:
        rows.append(
            {
                "module": panel.module,
                "validation_fraction": panel.validation_panel.validation_fraction,
                "metric_count": float(len(panel.quantitative_metrics)),
                "visual_artifacts": float(panel.visualization_panel.artifact_count),
                "evidence_links": float(len(panel.manuscript_evidence)),
                "gap_count": float(len(panel.known_gaps)),
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
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    image = ax.imshow(normalized.to_numpy(), aspect="auto", cmap="cividis", vmin=0, vmax=1)
    ax.set_title("BeeStack science-first methods dashboard", loc="left")
    ax.set_xticks(range(len(frame.columns)), frame.columns, rotation=25, ha="right")
    ax.set_yticks(range(len(frame.index)), frame.index)
    for row_index, module in enumerate(frame.index):
        for column_index, column in enumerate(frame.columns):
            raw = float(frame.loc[module, column])
            norm = float(normalized.loc[module, column])
            ax.text(
                column_index,
                row_index,
                f"{raw:.2g}",
                ha="center",
                va="center",
                color="white" if norm < 0.58 else "black",
                fontsize=8,
            )
    fig.colorbar(image, ax=ax, label="Column-normalized methods score")
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _methods_dashboard_detail(report: MethodsAnalysisReport, path: Path) -> Path:
    rows = []
    for panel in report.module_panels:
        rows.append(
            {
                "module": panel.module,
                "validation": panel.validation_panel.validation_fraction,
                "artifacts": panel.visualization_panel.artifact_count,
                "evidence": len(panel.manuscript_evidence),
                "gaps": len(panel.known_gaps),
                "boundary": panel.interpretation,
            }
        )
    fig, ax = plt.subplots(figsize=(12.4, 6.4))
    ax.axis("off")
    ax.text(
        0.02,
        0.96,
        "Methods dashboard detail: module evidence and explicit gaps",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=13,
        fontweight="bold",
        color="#111827",
    )
    headers = ("Module", "Validation", "Artifacts", "Evidence", "Gaps", "Boundary")
    widths = (0.12, 0.12, 0.12, 0.12, 0.08, 0.39)
    x_positions = np.cumsum((0.02, *widths[:-1]))
    for header, x in zip(headers, x_positions, strict=True):
        ax.text(x, 0.86, header, transform=ax.transAxes, fontsize=8.5, fontweight="bold")
    for row_index, row in enumerate(rows):
        y = 0.79 - row_index * 0.135
        ax.add_patch(
            plt.Rectangle(
                (0.015, y - 0.050),
                0.96,
                0.095,
                transform=ax.transAxes,
                facecolor="#F8FAFC" if row_index % 2 == 0 else "#FFFFFF",
                edgecolor="#E2E8F0",
                lw=0.5,
            )
        )
        ax.text(
            x_positions[0],
            y,
            str(row["module"]),
            transform=ax.transAxes,
            va="center",
            fontsize=9,
            fontweight="bold",
            color=module_color(str(row["module"])),
        )
        numeric = (
            format_compact_number(float(row["validation"])),
            str(row["artifacts"]),
            str(row["evidence"]),
            str(row["gaps"]),
        )
        for index, value in enumerate(numeric, start=1):
            ax.text(
                x_positions[index],
                y,
                value,
                transform=ax.transAxes,
                va="center",
                fontsize=8.4,
                color="#334155",
            )
        bounded_text(
            ax,
            float(x_positions[-1]),
            y + 0.038,
            row["boundary"],
            width=52,
            max_lines=3,
            fontsize=7.6,
            facecolor="#FFFFFF",
        )
    fig.text(
        0.5,
        0.025,
        "Detail companion to the normalized methods dashboard; counts are provenance and gap-routing evidence, not biological validation.",
        ha="center",
        va="bottom",
        fontsize=8,
        color="#475569",
    )
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _body_telemetry(
    records: tuple[dict[str, Any], ...],
    report: MethodsAnalysisReport,
    path: Path,
) -> Path:
    steps = _series(records, "step_index", default=np.arange(len(records), dtype=float))
    speed = _series(records, "body_speed_m_s")
    wing_power = _series(records, "wing_power_mw")
    energy = _series(records, "energy_j")
    body_panel = _panel(report, "BeeBody")
    metrics = body_panel.quantitative_metrics
    fig, axes = plt.subplots(2, 2, figsize=(10, 6.4))
    axes[0, 0].plot(steps, speed, color=module_color("BeeBody"), marker="o")
    apply_panel_style(axes[0, 0], title="COM speed witness", ylabel="m/s", grid_axis="both")
    axes[0, 1].plot(steps, wing_power, color=PALETTE[0], marker="s")
    apply_panel_style(axes[0, 1], title="Wingbeat power witness", ylabel="mW", grid_axis="both")
    axes[1, 0].plot(steps, energy, color=module_color("BeeBrain"), marker="^")
    apply_panel_style(axes[1, 0], title="Energy budget", ylabel="J", grid_axis="both")
    labels = ["bee_visual_score", "bee_silhouette_score", "wingbeat_frequency_hz"]
    raw_values = [float(metrics.get(label, 0.0)) for label in labels]
    scaled = np.log1p(np.abs(raw_values))
    if float(scaled.max()) > 0:
        scaled = scaled / float(scaled.max())
    bars = axes[1, 1].barh(
        [wrap_label(label.replace("_", " "), width=20, max_lines=2) for label in labels[::-1]],
        scaled[::-1],
        color=module_color("BeeMind"),
    )
    direct_label_bars(
        axes[1, 1],
        bars,
        tuple(raw_values[::-1]),
        horizontal=True,
    )
    axes[1, 1].set_xlim(0, 1.12)
    apply_panel_style(
        axes[1, 1],
        title="Morphology and wingbeat cues",
        xlabel="log1p-scaled value (raw label)",
        grid_axis="x",
    )
    for label, axis in zip(("A", "B", "C", "D"), axes.ravel(), strict=True):
        add_panel_label(axis, label)
    fig.suptitle("BeeBody methods telemetry and morphology diagnostics", y=0.995)
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))
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
    items = sorted(panel.quantitative_metrics.items(), key=lambda item: abs(item[1]))
    labels = [wrap_label(item[0].replace("_", " "), width=28, max_lines=2) for item in items]
    raw_values = np.asarray([float(item[1]) for item in items], dtype=float)
    scaled = np.log1p(np.abs(raw_values))
    max_scaled = float(scaled.max()) if scaled.size else 0.0
    if max_scaled > 0:
        scaled = scaled / max_scaled
    fig = plt.figure(figsize=(11, 5.8))
    grid = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0])
    ax = fig.add_subplot(grid[0, 0])
    ax_context = fig.add_subplot(grid[0, 1])
    y = np.arange(len(labels))
    ax.barh(y, scaled, color=module_color(module), alpha=0.88)
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 1.06)
    for row_index, (scaled_value, raw_value) in enumerate(zip(scaled, raw_values, strict=False)):
        ax.text(
            min(1.02, float(scaled_value) + 0.025),
            row_index,
            f"{raw_value:.3g}",
            va="center",
            ha="left",
            fontsize=7.5,
            color="#334155",
        )
    apply_panel_style(
        ax,
        title=title,
        xlabel="log1p-scaled metric magnitude (raw value labeled)",
        grid_axis="x",
    )
    add_panel_label(ax, "A")
    ax_context.axis("off")
    evidence = panel.manuscript_evidence[0]
    context_lines = (
        f"Validation fraction\n{panel.validation_panel.validation_fraction:.2f}",
        f"Linked visual artifacts\n{panel.visualization_panel.artifact_count}",
        f"Claim tier\n{evidence.claim_tier.replace('_', ' ')}",
        f"Availability\n{evidence.availability_status}",
        "Conservative boundary\n" + panel.interpretation,
    )
    for index, text in enumerate(context_lines):
        bounded_text(
            ax_context,
            0.02,
            0.93 - index * 0.18,
            text,
            width=36,
            max_lines=3,
            fontsize=9,
        )
    add_panel_label(ax_context, "B")
    fig.suptitle(f"{module}: methods evidence, validation, and claim boundary", y=0.975)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _niche_comb_thermal(
    records: tuple[dict[str, Any], ...],
    report: MethodsAnalysisReport,
    path: Path,
) -> Path:
    steps = _series(records, "step_index", default=np.arange(len(records), dtype=float))
    comb = _series(records, "comb_fraction")
    temp_error = _series(records, "brood_temperature_error_c")
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
        f"BeeNiche methods validation {panel.validation_panel.validation_fraction:.2f}",
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
    fig, ax = plt.subplots(figsize=(9.5, 5.0))
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
    ax2 = ax.twinx()
    ax2.plot(x, frame["validation_fraction"], color="#111827", marker="o", label="Validation")
    ax.set_xticks(x, frame["module"], rotation=20, ha="right")
    ax.set_ylabel("Count")
    ax2.set_ylabel("Validation fraction")
    ax2.set_ylim(0, 1.05)
    ax.set_title("Manuscript evidence index by module")
    apply_panel_style(ax, grid_axis="y")
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _panel(report: MethodsAnalysisReport, module: str):
    return next(panel for panel in report.module_panels if panel.module == module)


def _series(
    records: tuple[dict[str, Any], ...],
    key: str,
    default: np.ndarray | None = None,
) -> np.ndarray:
    if records:
        return np.asarray([float(row.get(key, index)) for index, row in enumerate(records)])
    if default is not None:
        return np.asarray(default, dtype=float)
    return np.asarray((0.0,), dtype=float)


def _validate_nonblank_image(path: Path) -> None:
    assert_nonblank_quality(path)
