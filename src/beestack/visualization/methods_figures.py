"""Methods-analysis figures and interactive dashboards."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from skimage import io as skio
from skimage.measure import label

from ..research import MethodsAnalysisReport


def generate_methods_figures(
    report: MethodsAnalysisReport,
    records: tuple[dict[str, Any], ...],
    output_dir: Path,
) -> list[Path]:
    """Generate publication-oriented methods-analysis figures."""

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        _repo_methods_dashboard(report, output_dir / "methods_repo_dashboard.png"),
        _body_telemetry(records, report, output_dir / "beebody_methods_telemetry_dashboard.png"),
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
        _manuscript_evidence_index(report, output_dir / "methods_manuscript_evidence_index.png"),
    ]
    for path in paths:
        _validate_nonblank_image(path)
    return paths


def write_interactive_methods_dashboard(
    report: MethodsAnalysisReport,
    output_dir: Path,
) -> list[Path]:
    """Write optional Plotly HTML methods-analysis dashboards."""

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
    fig, ax = plt.subplots(figsize=(10, 5.4))
    image = ax.imshow(normalized.to_numpy(), aspect="auto", cmap="cividis", vmin=0, vmax=1)
    ax.set_title("BeeStack science-first methods dashboard")
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
    axes[0, 0].plot(steps, speed, color="#0f766e", marker="o")
    axes[0, 0].set_title("COM speed witness")
    axes[0, 0].set_ylabel("m/s")
    axes[0, 1].plot(steps, wing_power, color="#d97706", marker="s")
    axes[0, 1].set_title("Wingbeat power witness")
    axes[0, 1].set_ylabel("mW")
    axes[1, 0].plot(steps, energy, color="#2563eb", marker="^")
    axes[1, 0].set_title("Energy budget")
    axes[1, 0].set_ylabel("J")
    labels = ["bee_visual_score", "bee_silhouette_score", "wingbeat_frequency_hz"]
    values = [metrics.get(label, 0.0) for label in labels]
    axes[1, 1].barh(labels[::-1], values[::-1], color="#7c3aed")
    axes[1, 1].set_title("Morphology and wingbeat cues")
    for axis in axes.ravel():
        axis.grid(alpha=0.22)
    fig.suptitle("BeeBody methods telemetry and morphology diagnostics", y=0.995)
    fig.tight_layout()
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
    labels = [item[0] for item in items]
    values = [item[1] for item in items]
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    ax.barh(labels, values, color="#2a9d8f")
    ax.set_title(title)
    ax.set_xlabel("Metric value")
    ax.grid(axis="x", alpha=0.22)
    ax.text(
        0.02,
        0.03,
        f"Validation {panel.validation_panel.validation_fraction:.2f}; "
        f"{panel.visualization_panel.artifact_count} linked visual artifacts",
        transform=ax.transAxes,
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": "#d1d5db", "alpha": 0.85},
    )
    fig.tight_layout()
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
    axes[0].plot(steps, comb, marker="s", color="#7c2d12")
    axes[0].set_title("Comb occupancy trajectory")
    axes[0].set_xlabel("Control step")
    axes[0].set_ylabel("Fraction")
    axes[1].plot(steps, temp_error, marker="o", color="#dc2626")
    axes[1].set_title("Brood thermal error")
    axes[1].set_xlabel("Control step")
    axes[1].set_ylabel("C")
    for axis in axes:
        axis.grid(alpha=0.22)
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
    ax.bar(x - 0.2, frame["evidence_links"], width=0.4, label="Evidence links", color="#2563eb")
    ax.bar(x + 0.2, frame["visual_artifacts"], width=0.4, label="Visual artifacts", color="#f59e0b")
    ax2 = ax.twinx()
    ax2.plot(x, frame["validation_fraction"], color="#111827", marker="o", label="Validation")
    ax.set_xticks(x, frame["module"], rotation=20, ha="right")
    ax.set_ylabel("Count")
    ax2.set_ylabel("Validation fraction")
    ax2.set_ylim(0, 1.05)
    ax.set_title("Manuscript evidence index by module")
    ax.grid(axis="y", alpha=0.22)
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
    image = skio.imread(path)
    if image.size == 0:
        raise ValueError(f"{path} is empty")
    grayscale = image[..., :3].mean(axis=2) if image.ndim == 3 else image
    foreground = np.abs(grayscale.astype(float) - float(np.median(grayscale))) > 1.0
    if int(label(foreground).max()) <= 0:
        raise ValueError(f"{path} appears blank")
