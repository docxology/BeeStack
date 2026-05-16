"""Empirical BeeBrain figure builders."""

from __future__ import annotations

from pathlib import Path
from textwrap import shorten

import matplotlib.pyplot as plt
import numpy as np

from ..brain import (
    AntennalMovementSummary,
    AtlasInventory,
    BeeBrainActivitySummary,
    BeeBrainAnatomySummary,
    BeeBrainDataCompletenessPanel,
    EmpiricalOdorResponsePanel,
    EmpiricalPanelStats,
    NeuropilAbbreviation,
    WaggleFollowerSummary,
)
from .figure_metadata import write_figure_sidecar


def generate_empirical_figures(
    panels: tuple[EmpiricalOdorResponsePanel, ...],
    panel_stats: tuple[EmpiricalPanelStats, ...],
    stack_alignment: dict[str, float],
    output_dir: Path,
    antennal_summaries: tuple[AntennalMovementSummary, ...] = (),
    anatomy_summary: BeeBrainAnatomySummary | None = None,
    anatomy_inventories: tuple[AtlasInventory, ...] = (),
    neuropil_abbreviations: tuple[NeuropilAbbreviation, ...] = (),
    activity_summary: BeeBrainActivitySummary | None = None,
    waggle_summary: WaggleFollowerSummary | None = None,
    data_completeness: BeeBrainDataCompletenessPanel | None = None,
) -> list[Path]:
    """Generate empirical data validation and stack-integration figures."""

    if not panels:
        raise ValueError("at least one empirical panel is required")
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        _panel_heatmap(panels[0], output_dir / "empirical_panel_heatmap.png"),
        _panel_quality_bars(panel_stats, output_dir / "empirical_panel_quality.png"),
        _stack_alignment_bars(stack_alignment, output_dir / "empirical_stack_alignment.png"),
    ]
    if antennal_summaries:
        paths.append(
            _antennal_movement_bars(
                antennal_summaries[0], output_dir / "empirical_antennal_movement.png"
            )
        )
    if anatomy_summary is not None and anatomy_inventories:
        paths.append(
            _anatomy_asset_bars(
                anatomy_summary,
                anatomy_inventories,
                output_dir / "empirical_anatomy_assets.png",
            )
        )
        if any(inventory.vrml_centroid is not None for inventory in anatomy_inventories):
            paths.append(
                _anatomy_projection(
                    anatomy_inventories,
                    output_dir / "empirical_anatomy_projection.png",
                )
            )
    if neuropil_abbreviations:
        paths.append(
            _neuropil_coverage_bars(
                neuropil_abbreviations,
                output_dir / "empirical_neuropil_coverage.png",
            )
        )
    if activity_summary is not None:
        paths.append(
            _activity_summary_bars(
                activity_summary,
                output_dir / "empirical_activity_summary.png",
            )
        )
    if waggle_summary is not None:
        paths.extend(
            [
                _waggle_follower_alignment(
                    waggle_summary,
                    output_dir / "waggle_follower_alignment.png",
                ),
                _waggle_phase_coupling(
                    waggle_summary,
                    output_dir / "waggle_phase_coupling.png",
                ),
                _waggle_recruitment_diagnostics(
                    waggle_summary,
                    output_dir / "beeswarm_waggle_recruitment_diagnostics.png",
                ),
            ]
        )
    if data_completeness is not None:
        paths.extend(
            [
                _brain_data_completeness_matrix(
                    data_completeness,
                    output_dir / "brain_data_completeness_matrix.png",
                ),
                _brain_multimodal_source_map(
                    data_completeness,
                    output_dir / "bee_brain_multimodal_source_map.png",
                ),
            ]
        )
    for path in paths:
        write_figure_sidecar(
            path,
            title=path.stem.replace("_", " ").title(),
            backend="Matplotlib empirical-data renderer",
            fidelity=_empirical_figure_fidelity(path.name),
            source_data="output/data/empirical_analysis.json",
            validation_status="nonblank empirical diagnostic",
            regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        )
    return paths


def _empirical_figure_fidelity(filename: str) -> str:
    """Classify empirical figures without implying calibration completeness."""

    if "waggle" in filename:
        return "empirical waggle/follower summary diagnostic"
    if "anatomy" in filename or "neuropil" in filename:
        return "empirical atlas/inventory summary diagnostic"
    if "completeness" in filename or "source_map" in filename:
        return "empirical dataset availability diagnostic"
    return "empirical panel summary diagnostic"


def _panel_heatmap(panel: EmpiricalOdorResponsePanel, path: Path) -> Path:
    matrix = np.asarray(panel.response_matrix, dtype=float)
    fig, ax = plt.subplots(figsize=(9, 5))
    image = ax.imshow(matrix, aspect="auto", cmap="viridis")
    ax.set_title(f"Empirical response panel: {_panel_label(panel.modality)}", fontsize=11)
    ax.set_xlabel("Stimulus")
    ax.set_ylabel("Channel")
    ax.set_xticks(range(len(panel.stimulus_labels)))
    ax.set_xticklabels(panel.stimulus_labels, rotation=45, ha="right", fontsize=8)
    channel_step = max(1, len(panel.channel_labels) // 12)
    channel_ticks = list(range(0, len(panel.channel_labels), channel_step))
    ax.set_yticks(channel_ticks)
    ax.set_yticklabels([panel.channel_labels[idx] for idx in channel_ticks], fontsize=8)
    fig.colorbar(image, ax=ax, label=panel.units)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _panel_quality_bars(stats: tuple[EmpiricalPanelStats, ...], path: Path) -> Path:
    top = sorted(stats, key=lambda row: row.mean_abs_response, reverse=True)[:10]
    labels = [row.modality[:42] for row in top]
    values = [row.mean_abs_response for row in top]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(labels[::-1], values[::-1], color="#2a9d8f")
    ax.set_title("Empirical panel mean absolute response")
    ax.set_xlabel("Mean absolute response")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _stack_alignment_bars(stack_alignment: dict[str, float], path: Path) -> Path:
    ranked = sorted(stack_alignment.items(), key=lambda item: item[1], reverse=True)[:12]
    labels = [label for label, _ in ranked]
    values = [value for _, value in ranked]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(labels[::-1], values[::-1], color="#e9a227")
    ax.set_title("BeeBrain alignment to empirical templates")
    ax.set_xlabel("Cosine alignment")
    ax.set_xlim(min(-1.0, min(values, default=0.0)), 1.0)
    ax.axvline(0, color="#222222", lw=0.8)
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _antennal_movement_bars(summary: AntennalMovementSummary, path: Path) -> Path:
    values = [
        summary.odor_on_fraction,
        summary.mean_abs_left_theta_deg / 180.0,
        summary.mean_abs_right_theta_deg / 180.0,
        min(1.0, summary.mean_abs_theta_derivative / 25.0),
        (summary.left_right_theta_correlation + 1.0) / 2.0,
    ]
    labels = [
        "Odor-on fraction",
        "Left theta deflection",
        "Right theta deflection",
        "Theta derivative drive",
        "Left/right synchrony",
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(
        labels[::-1],
        values[::-1],
        color=["#5b8e7d", "#f2b134", "#f2b134", "#d95d39", "#3a6ea5"][::-1],
    )
    ax.set_title("Jernigan empirical antennal active sensing")
    ax.set_xlabel("Normalized summary value")
    ax.set_xlim(0.0, 1.0)
    ax.grid(axis="x", alpha=0.2)
    ax.text(
        0.01,
        -0.18,
        f"{summary.row_count:,} frames, {summary.bee_count} bees, {summary.plume_count} plume classes",
        transform=ax.transAxes,
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _anatomy_asset_bars(
    summary: BeeBrainAnatomySummary, inventories: tuple[AtlasInventory, ...], path: Path
) -> Path:
    ranked = sorted(
        inventories,
        key=lambda inventory: inventory.total_uncompressed_bytes,
        reverse=True,
    )[:8]
    labels = [Path(inventory.local_path).name for inventory in ranked]
    values = [inventory.total_uncompressed_bytes / 1_000_000 for inventory in ranked]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(labels[::-1], values[::-1], color="#d99a28")
    ax.set_title("Honeybee Standard Brain atlas assets")
    ax.set_xlabel("Uncompressed archive contents (MB)")
    ax.grid(axis="x", alpha=0.2)
    ax.text(
        0.01,
        -0.18,
        (
            f"{summary.downloaded_asset_count}/{summary.asset_count} assets, "
            f"{summary.vrml_file_count} VRML files, {summary.tiff_file_count} TIFF files"
        ),
        transform=ax.transAxes,
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _neuropil_coverage_bars(abbreviations: tuple[NeuropilAbbreviation, ...], path: Path) -> Path:
    counts: dict[str, int] = {}
    for entry in abbreviations:
        counts[entry.region_class] = counts.get(entry.region_class, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    labels = [label for label, _ in ranked]
    values = [value for _, value in ranked]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(labels[::-1], values[::-1], color="#5f7f3f")
    ax.set_title("Honeybee Standard Brain neuropil abbreviation coverage")
    ax.set_xlabel("Abbreviation count")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _anatomy_projection(inventories: tuple[AtlasInventory, ...], path: Path) -> Path:
    vrml_items = [inventory for inventory in inventories if inventory.vrml_centroid is not None]
    fig, ax = plt.subplots(figsize=(7, 6))
    max_vertices = max((item.vrml_vertex_count for item in vrml_items), default=1)
    for inventory in vrml_items:
        centroid = inventory.vrml_centroid or (0.0, 0.0, 0.0)
        bounds_min = inventory.vrml_bounds_min
        bounds_max = inventory.vrml_bounds_max
        if bounds_min is not None and bounds_max is not None:
            width = max(bounds_max[0] - bounds_min[0], 1e-9)
            height = max(bounds_max[1] - bounds_min[1], 1e-9)
            ax.add_patch(
                plt.Rectangle(
                    (bounds_min[0], bounds_min[1]),
                    width,
                    height,
                    fill=False,
                    lw=1.0,
                    alpha=0.4,
                    color="#5b8e7d",
                )
            )
        size = 40 + 240 * inventory.vrml_vertex_count / max_vertices
        ax.scatter(centroid[0], centroid[1], s=size, alpha=0.75, color="#d99a28")
        ax.text(
            centroid[0],
            centroid[1],
            Path(inventory.local_path).stem.replace("_", " "),
            fontsize=8,
            ha="center",
            va="center",
        )
    ax.set_title("Honeybee Standard Brain VRML geometry projection")
    ax.set_xlabel("VRML X coordinate")
    ax.set_ylabel("VRML Y coordinate")
    ax.grid(alpha=0.2)
    ax.set_aspect("equal", adjustable="datalim")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _activity_summary_bars(summary: BeeBrainActivitySummary, path: Path) -> Path:
    values = [
        summary.mean_odor_separability,
        summary.calcium_inhibitory_fraction,
        summary.calcium_excitatory_fraction,
        min(1.0, summary.aftersmell_response_mean),
        summary.antennal_active_sensing_drive.get("theta_derivative_drive", 0.0),
    ]
    labels = [
        "Odor separability",
        "Calcium inhibitory fraction",
        "Calcium excitatory fraction",
        "Aftersmell response",
        "Antennal movement drive",
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(
        labels[::-1],
        values[::-1],
        color=["#3a6ea5", "#9467bd", "#2a9d8f", "#d95d39", "#5b8e7d"][::-1],
    )
    ax.set_title("BeeBrain empirical activity summary")
    ax.set_xlabel("Normalized summary value")
    ax.set_xlim(0.0, 1.0)
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _waggle_follower_alignment(summary: WaggleFollowerSummary, path: Path) -> Path:
    values = [
        abs(summary.follower_angle_midpoint_correlation),
        (summary.left_right_antenna_synchrony + 1.0) / 2.0,
        np.clip(summary.decoding_improvement_fraction, 0.0, 1.0),
        summary.straightness_mean,
        summary.confidence_score,
    ]
    labels = [
        "Angle-midpoint coupling",
        "Left/right synchrony",
        "Decoding improvement",
        "Follower straightness",
        "BeeStack confidence",
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(labels[::-1], values[::-1], color="#9a6a1f")
    ax.set_title("Waggle follower empirical antennal alignment")
    ax.set_xlabel("Normalized score")
    ax.set_xlim(0.0, 1.0)
    ax.grid(axis="x", alpha=0.2)
    ax.text(
        0.01,
        -0.18,
        f"{summary.track_count} follower tracks, {summary.feature_row_count:,} feature rows",
        transform=ax.transAxes,
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _waggle_phase_coupling(summary: WaggleFollowerSummary, path: Path) -> Path:
    labels = ["Left antenna", "Right antenna", "Midpoint", "Dancer gravity", "Follower angle"]
    values = [
        summary.mean_left_antenna_deg,
        summary.mean_right_antenna_deg,
        summary.mean_antenna_midpoint_deg,
        summary.mean_dancer_angle_to_gravity_deg,
        summary.mean_angle_to_dancer_deg,
    ]
    theta = np.deg2rad(values)
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="polar")
    ax.scatter(theta, np.ones(len(theta)), s=90, color="#d99a28")
    for angle, label in zip(theta, labels, strict=True):
        ax.plot([angle, angle], [0.0, 1.0], lw=1.2, alpha=0.65)
        ax.text(angle, 1.12, label, fontsize=8, ha="center", va="center")
    ax.set_title("Waggle follower phase and antenna coupling")
    ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _waggle_recruitment_diagnostics(summary: WaggleFollowerSummary, path: Path) -> Path:
    error_values = [
        summary.no_antennae_mean_abs_error_deg,
        summary.mean_abs_vector_error_deg,
        summary.both_antennae_mean_abs_error_deg,
    ]
    labels = ["No antennae", "All model rows", "Both antennae"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, error_values, color=["#9ca3af", "#d99a28", "#2a9d8f"])
    ax.set_title("BeeSwarm waggle recruitment decoding error inputs")
    ax.set_ylabel("Mean absolute vector error (deg)")
    ax.grid(axis="y", alpha=0.2)
    ax.text(
        0.02,
        0.93,
        f"confidence={summary.confidence_score:.2f}; improvement={summary.decoding_improvement_fraction:.2f}",
        transform=ax.transAxes,
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _brain_data_completeness_matrix(panel: BeeBrainDataCompletenessPanel, path: Path) -> Path:
    modules = sorted(panel.module_modality_matrix)
    modalities = sorted({key for values in panel.module_modality_matrix.values() for key in values})
    matrix = np.array(
        [
            [panel.module_modality_matrix[module].get(modality, 0) for modality in modalities]
            for module in modules
        ],
        dtype=float,
    )
    fig, ax = plt.subplots(figsize=(10, 5.5))
    image = ax.imshow(matrix, aspect="auto", cmap="YlGnBu")
    ax.set_title("BeeBrain curated source completeness matrix")
    ax.set_xlabel("Modality family")
    ax.set_ylabel("Module target")
    ax.set_xticks(range(len(modalities)))
    ax.set_xticklabels(modalities, rotation=35, ha="right", fontsize=8)
    ax.set_yticks(range(len(modules)))
    ax.set_yticklabels(modules, fontsize=8)
    fig.colorbar(image, ax=ax, label="Curated source count")
    ax.text(
        0.01,
        -0.22,
        f"downloaded={panel.downloaded_fraction:.2f}; parseable={panel.parseable_fraction:.2f}",
        transform=ax.transAxes,
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _brain_multimodal_source_map(panel: BeeBrainDataCompletenessPanel, path: Path) -> Path:
    labels = sorted(panel.modality_counts)
    values = [panel.modality_counts[label] for label in labels]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(labels[::-1], values[::-1], color="#3a6ea5")
    ax.set_title("BeeBrain multimodal empirical source map")
    ax.set_xlabel("Curated source count")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _panel_label(modality: str) -> str:
    parts = [part for part in modality.split(":") if part]
    label = parts[-2] if len(parts) >= 2 else modality
    return shorten(label, width=54, placeholder="...")
