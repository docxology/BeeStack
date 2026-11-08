"""BeeStack publication figure builders — submodule."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

from .figures_common import (
    _numeric_series,
    _policy_series,
    _steps,
)
from .style import (
    add_figure_note,
    apply_panel_style,
    format_compact_number,
    module_color,
    wrap_label,
)


def _energy_timeseries(records: list[dict[str, Any]], path: Path) -> Path:
    steps = _steps(records)
    energy = _numeric_series(records, "energy_j")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(steps, energy, marker="o", color=module_color("BeeBody"), label="Energy (J)")
    ax.set_xlabel("Control step")
    ax.set_ylabel("Energy (J)")
    ax.ticklabel_format(axis="y", style="plain", useOffset=False)
    ax.set_title("Reduced body energy across control steps", loc="left")
    # Direct annotation of the total energy change so the reader does not
    # have to subtract endpoint values from the axis.
    if len(energy) >= 2:
        change = energy[-1] - energy[0]
        sign = "+" if change > 0 else ""
        ax.text(
            0.97,
            0.90,
            f"Endpoint change: {sign}{format_compact_number(change)} J",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=8,
            color="#334155",
        )
    apply_panel_style(ax, grid_axis="both")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _comb_timeseries(records: list[dict[str, Any]], path: Path) -> Path:
    steps = _steps(records)
    comb = _numeric_series(records, "comb_fraction")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(steps, comb, marker="s", color=module_color("BeeNiche"), label="Comb fraction")
    ax.set_xlabel("Control step")
    ax.set_ylabel("Comb occupancy fraction")
    ax.set_title("Reduced comb occupancy across control steps", loc="left")
    ax.set_ylim(0, max(0.1, max(comb) * 1.2))
    apply_panel_style(ax, grid_axis="both")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _module_coverage(module_names: list[str], path: Path) -> Path:
    modules = module_names or ["BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"]
    colors = [module_color(module) for module in modules]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter([1] * len(modules), range(len(modules)), c=colors, s=110, zorder=3)
    ax.set_yticks(range(len(modules)), modules)
    ax.invert_yaxis()
    ax.set_xticks([0, 1], ["0", "1"])
    ax.set_xlim(-0.05, 1.15)
    apply_panel_style(
        ax, title="Module contract inventory", xlabel="Listed module (binary)", grid_axis="x"
    )
    add_figure_note(
        fig,
        "Presence in the supplied module list is not test coverage or biological validation.",
        y=0.015,
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _body_motion_power_phase(records: list[dict[str, Any]], path: Path) -> Path:
    steps = _steps(records)
    speed = _numeric_series(records, "body_speed_m_s")
    wing_power = _numeric_series(records, "wing_power_mw")
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    points = ax.scatter(speed, wing_power, c=steps, cmap="viridis", s=70, edgecolor="#111827")
    ax.plot(speed, wing_power, color="#64748b", lw=1.0, alpha=0.55)
    fig.colorbar(points, ax=ax, label="Control step")
    ax.set_xlabel("Body speed (m/s)")
    ax.set_ylabel("Wing power (mW)")
    ax.set_title("Reduced motion–power trajectory", loc="left")
    apply_panel_style(ax, grid_axis="both")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _brain_empirical_alignment(records: list[dict[str, Any]], path: Path) -> Path:
    steps = _steps(records)
    alignment = _numeric_series(records, "dominant_empirical_alignment", default=None)
    odors = [str(row.get("dominant_empirical_odor", "")) for row in records] or [""]
    fig, ax = plt.subplots(figsize=(7, 4))
    observed = [value for value in alignment if value is not None]
    samples = np.asarray(alignment, dtype=float)
    ax.plot(steps, samples, marker="o", color="#1d4ed8", lw=2, label="Template alignment")
    if not observed:
        ax.text(
            0.5,
            0.5,
            "Alignment unavailable\nNo observed template-alignment values",
            ha="center",
            va="center",
            transform=ax.transAxes,
            color="#475569",
            fontsize=11,
        )
    odors_present = [odor for odor in odors if odor]
    if odors_present:
        # Name the dominant empirical odor in a legend entry rather than a
        # marginal annotation that clips against the axes edge.
        ax.plot(
            [],
            [],
            linestyle="none",
            marker="s",
            color="#93c5fd",
            label=f"dominant empirical odor: {odors_present[-1]}",
        )
        ax.legend(loc="lower right", fontsize=8)
    ax.set_ylim(-1.05, 1.05)
    ax.set_xlim(steps[0] - 0.5, steps[-1] + 0.5)
    ax.set_xlabel("Control step")
    ax.set_ylabel("Cosine template alignment")
    ax.set_title("Odor-template alignment — availability preserved", loc="left")
    apply_panel_style(ax, grid_axis="both")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _mind_policy_timeline(records: list[dict[str, Any]], path: Path) -> Path:
    steps = _steps(records)
    policies, encoded = _policy_series(records)
    labels = list(dict.fromkeys(policies))
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    ax.step(steps, encoded, where="mid", color=module_color("BeeMind"), lw=2)
    ax.scatter(steps, encoded, color=module_color("BeeMind"), s=35, zorder=3)
    ax.set_yticks(range(len(labels)), labels)
    ax.set_ylabel("Selected policy")
    ax.set_xlabel("Control step")
    ax.set_title("Reduced controller: selected policy", loc="left")
    apply_panel_style(ax, grid_axis="x")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _swarm_recruitment_allocation(records: list[dict[str, Any]], path: Path) -> Path:
    steps = _steps(records)
    recruited = _numeric_series(records, "recruited_followers")
    pheromone = _numeric_series(records, "mean_pheromone")
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 5.8), sharex=True)
    axes[0].bar(steps, recruited, color=module_color("BeeSwarm"), width=0.7)
    axes[0].set_ylabel("Followers")
    axes[0].set_title("Reduced recruitment and shared-field state", loc="left")
    axes[1].plot(steps, pheromone, color="#0f766e", marker="o", label="Mean pheromone")
    axes[1].set_ylabel("Mean pheromone (a.u.)")
    axes[1].set_xlabel("Control step")
    for axis in axes:
        apply_panel_style(axis, grid_axis="y")
    add_figure_note(
        fig,
        "Fixed synthetic dance scenario; follower counts are not calibrated colony recruitment.",
        y=0.015,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _niche_thermal_comb_panel(records: list[dict[str, Any]], path: Path) -> Path:
    steps = _steps(records)
    comb = _numeric_series(records, "comb_fraction")
    error = _numeric_series(records, "brood_temperature_error_c")
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 5.8), sharex=True)
    axes[0].plot(steps, comb, color=module_color("BeeNiche"), marker="s")
    axes[0].set_ylabel("Comb fraction")
    axes[0].set_ylim(0, max(0.1, max(comb) * 1.2))
    axes[0].set_title("Reduced comb and brood-temperature diagnostics", loc="left")
    axes[1].plot(steps, error, color="#b91c1c", marker="o")
    axes[1].set_ylabel("Brood temperature error (°C)")
    axes[1].set_xlabel("Control step")
    for axis in axes:
        apply_panel_style(axis, grid_axis="y")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _stack_graphical_abstract(module_names: list[str], path: Path) -> Path:
    modules = module_names or ["BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"]
    nodes = {
        "BeeMind": (0.48, 0.73, "Belief → policy"),
        "BeeBody": (0.82, 0.73, "Reduced body step"),
        "BeeBrain": (0.82, 0.30, "Observation processing"),
        "BeeSwarm": (0.14, 0.30, "Recruitment + field decay"),
        "BeeNiche": (0.48, 0.30, "Reduced thermal update"),
    }
    fig, ax = plt.subplots(figsize=(11.4, 6.0))
    ax.axis("off")
    ax.text(
        0.14,
        0.73,
        "Fixed synthetic\nDanceVector",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=11,
        color="#111827",
        bbox={"boxstyle": "round,pad=0.65", "facecolor": "#F1F5F9", "edgecolor": "#64748B"},
    )
    edges = (
        (None, "BeeMind", (0.26, 0.73), (0.36, 0.73), "belief update", (0.31, 0.83)),
        (None, "BeeSwarm", (0.14, 0.61), (0.14, 0.41), "broadcast", (0.14, 0.51)),
        ("BeeMind", "BeeBody", (0.60, 0.73), (0.70, 0.73), "Action", (0.65, 0.83)),
        ("BeeBody", "BeeBrain", (0.82, 0.61), (0.82, 0.41), "Observation", (0.82, 0.51)),
    )
    for source, target, start, end, label, label_xy in edges:
        if target not in modules or (source is not None and source not in modules):
            continue
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                transform=ax.transAxes,
                arrowstyle="-|>",
                mutation_scale=14,
                lw=1.5,
                color="#475569",
            )
        )
        ax.text(
            *label_xy,
            label,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=9,
            color="#111827",
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 2},
        )
    for module, (x, y, role) in nodes.items():
        if module not in modules:
            continue
        color = module_color(module)
        ax.add_patch(
            Rectangle(
                (x - 0.12, y - 0.11),
                0.24,
                0.22,
                transform=ax.transAxes,
                facecolor="#F8FAFC",
                edgecolor=color,
                lw=1.6,
            )
        )
        ax.add_patch(
            Rectangle(
                (x - 0.12, y - 0.11), 0.008, 0.22, transform=ax.transAxes, facecolor=color, lw=0
            )
        )
        ax.text(
            x,
            y + 0.035,
            module,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            weight="bold",
            color="#111827",
        )
        ax.text(
            x,
            y - 0.045,
            wrap_label(role, width=23),
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=9,
            color="#334155",
        )
    ax.text(
        0.48,
        0.49,
        "Independent niche\nupdate per tick",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=9,
        color="#64748B",
    )
    ax.text(
        0.5,
        0.065,
        "SimulationRecord: native-unit telemetry + nullable empirical alignment",
        transform=ax.transAxes,
        ha="center",
        fontsize=10,
        color="#334155",
    )
    ax.set_title("BeeStack: the executed reduced scenario", loc="left", pad=16)
    add_figure_note(
        fig,
        "Execution schematic, not biological validation. No BrainState → policy feedback is asserted.\nSeparate pose/contact scenes do not calibrate this reduced loop; empirical inputs are optional and gated.",
        y=0.02,
    )
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path
