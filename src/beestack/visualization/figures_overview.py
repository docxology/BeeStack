"""BeeStack publication figure builders — submodule."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

from .style import module_color


def _contract_network(path: Path) -> Path:
    modules = ["BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"]
    payloads = [
        ("BeeBody", "BeeBrain", "Observation"),
        ("BeeBrain", "BeeMind", "BrainState"),
        ("BeeMind", "BeeBody", "Action"),
        ("BeeMind", "BeeSwarm", "BeliefState"),
        ("BeeSwarm", "BeeNiche", "BeeAgent/PheromoneField"),
        ("BeeNiche", "BeeMind", "CombGrid metrics"),
    ]
    colors = [module_color(module) for module in modules]
    angles = np.linspace(np.pi / 2, np.pi / 2 - 2 * np.pi, len(modules), endpoint=False)
    positions = {
        module: (0.5 + 0.34 * np.cos(angle), 0.52 + 0.34 * np.sin(angle))
        for module, angle in zip(modules, angles, strict=False)
    }
    fig, ax = plt.subplots(figsize=(6.8, 6.2))
    ax.axis("off")
    for source, target, label in payloads:
        start = positions[source]
        end = positions[target]
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                transform=ax.transAxes,
                arrowstyle="->",
                mutation_scale=12,
                lw=1.25,
                color="#475569",
                alpha=0.82,
                connectionstyle="arc3,rad=0.16",
            )
        )
        mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        ax.text(mid[0], mid[1], label, transform=ax.transAxes, fontsize=7, ha="center")
    for index, module in enumerate(modules):
        x, y = positions[module]
        ax.add_patch(
            Circle(
                (x, y),
                0.075,
                transform=ax.transAxes,
                facecolor=colors[index],
                edgecolor="#111827",
                lw=1.1,
                alpha=0.94,
            )
        )
        ax.text(
            x,
            y,
            module.replace("Bee", "Bee\n"),
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=8,
            color="white",
        )
    ax.set_title("BeeStack cross-layer API contract network")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _scale_ladder(path: Path) -> Path:
    rows = [
        ("Body", "milliseconds", "joints, wings, sensors", module_color("BeeBody")),
        ("Brain", "10-100 ms", "AL/MB/CX activity", module_color("BeeBrain")),
        ("Mind", "0.1-1 s", "beliefs and policies", module_color("BeeMind")),
        ("Swarm", "seconds-minutes", "dance, pheromone, tasks", module_color("BeeSwarm")),
        ("Niche", "minutes-days", "comb, heat, landscape", module_color("BeeNiche")),
    ]
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.axis("off")
    for index, (level, timescale, substrate, color) in enumerate(rows):
        y = 0.82 - index * 0.16
        ax.add_patch(
            Rectangle(
                (0.08, y - 0.045), 0.84, 0.085, transform=ax.transAxes, color=color, alpha=0.82
            )
        )
        ax.text(
            0.12,
            y,
            f"Bee{level}",
            transform=ax.transAxes,
            va="center",
            fontsize=11,
            color="white",
            weight="bold",
        )
        ax.text(0.36, y, timescale, transform=ax.transAxes, va="center", fontsize=10, color="white")
        ax.text(0.58, y, substrate, transform=ax.transAxes, va="center", fontsize=10, color="white")
    ax.set_title("BeeStack scale ladder")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _evidence_ladder(path: Path) -> Path:
    rows = [
        (
            "Strict rendered physics",
            "FlyBody/MuJoCo",
            "contact reports + visual signature",
            "small-scene contacts only",
            "scene evidence",
            module_color("BeeBody"),
        ),
        (
            "Empirical availability",
            "BeeBrain source registry",
            "DOI/source status + parser status",
            "availability, not synthetic traces",
            "source evidence",
            module_color("BeeBrain"),
        ),
        (
            "Reduced validated kernels",
            "Mind, swarm, niche",
            "finite diagnostics + scenario sweeps",
            "kernel behavior, not calibration",
            "kernel evidence",
            module_color("BeeMind"),
        ),
        (
            "Compatibility summaries",
            "BEEHAVE/Hiveopolis adapters",
            "schema/parity report fields",
            "compatibility, not validation",
            "adapter evidence",
            module_color("BeeSwarm"),
        ),
        (
            "Blocked digital twin",
            "readiness review",
            "assimilation/residual/uncertainty gaps",
            "target only, not ready",
            "gap evidence",
            "#C43C39",
        ),
    ]
    fig, ax = plt.subplots(figsize=(12.2, 5.8))
    ax.axis("off")
    headers = ("Evidence tier", "Backend/source", "Validation recorded", "Not supported")
    for x, header in zip((0.07, 0.34, 0.56, 0.76), headers, strict=True):
        ax.text(
            x,
            0.875,
            header,
            transform=ax.transAxes,
            va="center",
            fontsize=9,
            color="#111827",
            weight="bold",
        )
    for index, (tier, source, validation, boundary, badge, color) in enumerate(rows):
        y = 0.78 - index * 0.135
        ax.add_patch(
            Rectangle(
                (0.045, y - 0.050),
                0.91,
                0.098,
                transform=ax.transAxes,
                facecolor="#F8FAFC" if index % 2 == 0 else "#FFFFFF",
                edgecolor="#CBD5E1",
                lw=0.8,
            )
        )
        ax.add_patch(
            Rectangle(
                (0.045, y - 0.050),
                0.012,
                0.098,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor=color,
                lw=0,
            )
        )
        ax.text(
            0.07,
            y,
            tier,
            transform=ax.transAxes,
            va="center",
            fontsize=9.5,
            color="#111827",
            weight="bold",
        )
        ax.text(
            0.34,
            y,
            source,
            transform=ax.transAxes,
            va="center",
            fontsize=8.5,
            color="#111827",
        )
        ax.text(
            0.56,
            y,
            validation,
            transform=ax.transAxes,
            va="center",
            fontsize=8.2,
            color="#111827",
        )
        ax.text(
            0.76,
            y,
            boundary,
            transform=ax.transAxes,
            va="center",
            fontsize=8.0,
            color="#111827",
        )
        ax.text(
            0.20,
            y - 0.028,
            badge,
            transform=ax.transAxes,
            va="center",
            fontsize=6.8,
            color=color,
            weight="bold",
        )
    audit_badges = ("caption contract", "sidecar metadata", "DOI/source links", "gap language")
    for index, badge in enumerate(audit_badges):
        x = 0.18 + index * 0.17
        ax.add_patch(
            Rectangle(
                (x, 0.105),
                0.14,
                0.036,
                transform=ax.transAxes,
                facecolor="#EEF2FF",
                edgecolor="#A5B4FC",
                lw=0.7,
            )
        )
        ax.text(
            x + 0.07,
            0.123,
            badge,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=7.2,
            color="#312E81",
        )
    ax.text(
        0.5,
        0.05,
        "Reading rule: rows are evidence contracts; badges are the audit gates that keep higher-tier claims as gaps.",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        color="#334155",
    )
    ax.set_title("BeeStack evidence ladder: what the visuals can and cannot support")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path
