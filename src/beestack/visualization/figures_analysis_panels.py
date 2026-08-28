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
    bounded_text,
    module_color,
    status_color,
    wrap_label,
)


def _style_secondary_axis(axis: Any) -> None:
    """Restyle a twinx axis so it reads as part of the same panel."""

    axis.spines["top"].set_visible(False)
    axis.grid(False)


def _add_panel_legend(figure: Any, handles: list[Any], labels: list[str], axis: Any) -> None:
    """Attach a compact legend for dual-axis panels so series are identifiable."""

    if handles:
        figure.legend(
            handles,
            labels,
            loc="upper right",
            bbox_to_anchor=(0.98, 0.97),
            bbox_transform=axis.transAxes,
            fontsize=8,
            handlelength=1.6,
        )


def _energy_timeseries(records: list[dict[str, Any]], path: Path) -> Path:
    steps = _steps(records)
    energy = _numeric_series(records, "energy_j")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(steps, energy, marker="o", color="#0f766e", label="Energy (J)")
    ax.set_xlabel("Control step")
    ax.set_ylabel("Energy (J)")
    ax.set_title("BeeBody energy across integrated BeeStack run")
    # Direct annotation of the total energy change so the reader does not
    # have to subtract endpoint values from the axis.
    if len(energy) >= 2:
        change = energy[-1] - energy[0]
        sign = "+" if change > 0 else ""
        ax.text(
            0.97,
            0.90,
            f"change: {sign}{change:.2f} J over {len(steps) - 1} steps",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=8,
            color="#0f766e",
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
    ax.plot(steps, comb, marker="s", color="#7c2d12", label="Comb fraction")
    ax.set_xlabel("Control step")
    ax.set_ylabel("Comb occupancy fraction")
    ax.set_title("BeeNiche comb occupancy witness")
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
    ax.bar(modules, [1] * len(modules), color=colors[: len(modules)])
    ax.set_ylabel("Implemented v0 contract")
    apply_panel_style(
        ax,
        title="BeeStack module contract coverage",
        ylabel="Implemented v0 contract",
    )
    ax.set_xticks(range(len(modules)), modules, rotation=20, ha="right")
    fig.tight_layout()
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
    for step, x, y in zip(steps, speed, wing_power, strict=False):
        ax.text(x, y, str(step), fontsize=7, ha="center", va="center", color="white")
    fig.colorbar(points, ax=ax, label="Control step")
    ax.set_xlabel("Body speed (m/s)")
    ax.set_ylabel("Wing power (mW)")
    ax.set_title("BeeBody motion-power phase portrait")
    apply_panel_style(ax, grid_axis="both")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _brain_empirical_alignment(records: list[dict[str, Any]], path: Path) -> Path:
    steps = _steps(records)
    alignment = _numeric_series(records, "dominant_empirical_alignment")
    odors = [str(row.get("dominant_empirical_odor", "")) for row in records] or [""]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(steps, alignment, marker="o", color="#1d4ed8", lw=2, label="Template alignment")
    ax.fill_between(steps, alignment, color="#bfdbfe", alpha=0.45)
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
    ax.set_ylim(0, max(1.0, max(alignment) * 1.15))
    ax.set_xlim(left=steps[0] - 0.15 * max(1, steps[-1] - steps[0]))
    ax.set_xlabel("Control step")
    ax.set_ylabel("Template alignment (fraction)")
    ax.set_title("BeeBrain empirical odor-template alignment")
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
    ax.step(steps, encoded, where="mid", color="#9333ea", lw=2)
    ax.scatter(steps, encoded, color="#f97316", s=42, zorder=3)
    ax.set_yticks(range(len(labels)), labels)
    ax.set_ylabel("Selected policy")
    ax.set_xlabel("Control step")
    ax.set_title("BeeMind selected-policy timeline")
    apply_panel_style(ax, grid_axis="x")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _swarm_recruitment_allocation(records: list[dict[str, Any]], path: Path) -> Path:
    steps = _steps(records)
    recruited = _numeric_series(records, "recruited_followers")
    pheromone = _numeric_series(records, "mean_pheromone")
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(steps, recruited, color="#f59e0b", alpha=0.82, label="Recruited followers")
    ax.set_xlabel("Control step")
    ax.set_ylabel("Followers")
    ax2 = ax.twinx()
    ax2.plot(steps, pheromone, color="#0f766e", marker="o", label="Mean pheromone (a.u.)")
    ax2.set_ylabel("Mean pheromone (a.u.)")
    ax.set_title("BeeSwarm recruitment and shared-field state")
    ax.bar_label(bars, fmt="%.0f", fontsize=7, padding=2)
    apply_panel_style(ax, grid_axis="y")
    _style_secondary_axis(ax2)
    _add_panel_legend(
        fig,
        [bars, ax2.lines[0]],
        ["Recruited followers", "Mean pheromone (a.u.)"],
        ax,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _niche_thermal_comb_panel(records: list[dict[str, Any]], path: Path) -> Path:
    steps = _steps(records)
    comb = _numeric_series(records, "comb_fraction")
    error = _numeric_series(records, "brood_temperature_error_c")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(steps, comb, color="#7c2d12", marker="s", label="Comb fraction")
    ax.set_xlabel("Control step")
    ax.set_ylabel("Comb fraction")
    ax.set_ylim(0, max(0.1, max(comb) * 1.2))
    ax2 = ax.twinx()
    ax2.plot(steps, error, color="#dc2626", marker="o", label="Brood temperature error")
    ax2.set_ylabel("Brood temperature error (°C)")
    ax.set_title("BeeNiche comb and brood-thermal diagnostics")
    apply_panel_style(ax, grid_axis="both")
    _style_secondary_axis(ax2)
    _add_panel_legend(
        fig,
        [ax.lines[0], ax2.lines[0]],
        ["Comb fraction", "Brood temperature error (°C)"],
        ax,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _stack_graphical_abstract(module_names: list[str], path: Path) -> Path:
    modules = module_names or ["BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"]
    lane_text = {
        "BeeBody": (
            "FlyBody/MuJoCo assets, contact telemetry, reduced energetics",
            "Observation and body-state witness",
            "Strict small-scene render plus reduced telemetry",
        ),
        "BeeBrain": (
            "HSB atlas, odor panels, waggle/follower sources, parseability report",
            "BrainState and empirical availability witness",
            "Structural projectome and registered source gaps",
        ),
        "BeeMind": (
            "Finite expected-free-energy terms and deterministic policy checks",
            "BeliefState and selected policy",
            "Reduced controller, not a learned biological model",
        ),
        "BeeSwarm": (
            "Dance/contact scene outputs, pheromone field, BEEHAVE anchor",
            "BeeAgent allocation and follower diagnostics",
            "No colony-scale recruitment validation",
        ),
        "BeeNiche": (
            "Comb grid, brood-temperature error, forage and adapter records",
            "CombGrid, thermal, and niche-context witness",
            "Reduced niche context, not full hive ecology",
        ),
    }
    fig, ax = plt.subplots(figsize=(12.2, 5.35))
    ax.axis("off")
    ax.text(
        0.03,
        0.965,
        "BeeStack graphical abstract: local evidence -> typed contracts -> claim boundaries",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=13,
        fontweight="bold",
        color="#111827",
    )
    headers = (
        ("Module", 0.045),
        ("Local evidence", 0.238),
        ("Typed contract", 0.498),
        ("Boundary", 0.735),
    )
    for header, x in headers:
        ax.text(x, 0.855, header, transform=ax.transAxes, fontsize=8.8, fontweight="bold")
    y_positions = np.linspace(0.755, 0.275, len(modules))
    for index, (module, y) in enumerate(zip(modules, y_positions, strict=False)):
        color = module_color(module)
        evidence, contract, boundary = lane_text.get(
            module, ("Generated records", module, "Gap bounded")
        )
        ax.add_patch(
            Rectangle(
                (0.03, y - 0.055),
                0.16,
                0.092,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor="#111827",
                lw=0.9,
                alpha=0.92,
            )
        )
        ax.text(
            0.115,
            y,
            module,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="white",
        )
        bounded_text(ax, 0.232, y + 0.038, evidence, width=32, max_lines=3, fontsize=7.9)
        bounded_text(
            ax,
            0.492,
            y + 0.038,
            contract,
            width=30,
            max_lines=3,
            fontsize=7.9,
            facecolor="#FFFFFF",
        )
        bounded_text(
            ax,
            0.728,
            y + 0.038,
            boundary,
            width=31,
            max_lines=3,
            fontsize=7.8,
            facecolor="#FFF7ED",
            edgecolor="#FED7AA",
        )
        for start_x, end_x in ((0.195, 0.225), (0.455, 0.485), (0.690, 0.720)):
            ax.add_patch(
                FancyArrowPatch(
                    (start_x, y),
                    (end_x, y),
                    transform=ax.transAxes,
                    arrowstyle="-|>",
                    mutation_scale=11,
                    lw=1.0,
                    color="#334155",
                )
            )
        if index < len(modules) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (0.595, y - 0.055),
                    (0.595, y_positions[index + 1] + 0.055),
                    transform=ax.transAxes,
                    arrowstyle="-|>",
                    mutation_scale=11,
                    lw=1.0,
                    color="#64748B",
                    linestyle="--",
                )
            )
    legend_items = (
        ("sidecar metadata", "available"),
        ("plot-data JSON", "structural"),
        ("unsupported boundary", "warning"),
    )
    for index, (label, status) in enumerate(legend_items):
        x = 0.20 + index * 0.21
        ax.add_patch(
            Rectangle(
                (x, 0.075),
                0.028,
                0.024,
                transform=ax.transAxes,
                facecolor=status_color(status),
                edgecolor="#111827",
                lw=0.5,
            )
        )
        ax.text(
            x + 0.036,
            0.087,
            wrap_label(label, width=22),
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=8.4,
            color="#334155",
        )
    add_figure_note(
        fig,
        "Boundary rule: arrows are typed software/data contracts and evidence routing, not biological validation or digital-twin readiness.",
        y=0.018,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path
