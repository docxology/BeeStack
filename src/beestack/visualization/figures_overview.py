"""Architecture and evidence-boundary schematics (not run measurements)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

from ..config import config_from_mapping
from ..contracts import stack_contracts
from .style import add_figure_note, module_color, wrap_label


def _contract_network(path: Path) -> Path:
    # Default configuration resolves endpoint/payload declarations only. No rate
    # or timing from that configuration is presented as an executed measurement.
    positions = {
        "BeeBody": (0.14, 0.64),
        "BeeBrain": (0.50, 0.64),
        "BeeMind": (0.86, 0.64),
        "BeeSwarm": (0.71, 0.26),
        "BeeNiche": (0.29, 0.26),
    }
    fig, ax = plt.subplots(figsize=(10.8, 6.0))
    ax.axis("off")
    routes = {
        ("BeeBody", "BeeBrain"): ((0.24, 0.64), (0.40, 0.64), (0.32, 0.69), "arc3"),
        ("BeeBrain", "BeeMind"): ((0.60, 0.64), (0.76, 0.64), (0.68, 0.69), "arc3"),
        ("BeeMind", "BeeBody"): ((0.86, 0.72), (0.14, 0.72), (0.50, 0.91), "arc3,rad=0.20"),
        ("BeeBrain", "BeeSwarm"): ((0.50, 0.56), (0.66, 0.34), (0.52, 0.44), "arc3"),
        ("BeeSwarm", "BeeMind"): ((0.77, 0.34), (0.86, 0.56), (0.87, 0.43), "arc3"),
        ("BeeSwarm", "BeeNiche"): ((0.61, 0.26), (0.39, 0.26), (0.50, 0.20), "arc3"),
        ("BeeNiche", "BeeBody"): ((0.23, 0.34), (0.14, 0.56), (0.19, 0.43), "arc3"),
    }
    for edge in stack_contracts(config_from_mapping({})):
        start, end, label_position, connection = routes[(edge.source, edge.target)]
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                transform=ax.transAxes,
                arrowstyle="-|>",
                mutation_scale=14,
                lw=1.5,
                color="#475569",
                connectionstyle=connection,
            )
        )
        ax.text(
            *label_position,
            wrap_label(edge.payload, width=22),
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=9,
            color="#111827",
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 2.5},
        )
    for module, (x, y) in positions.items():
        color = module_color(module)
        ax.add_patch(
            Rectangle(
                (x - 0.10, y - 0.08),
                0.20,
                0.16,
                transform=ax.transAxes,
                facecolor="#F8FAFC",
                edgecolor=color,
                lw=1.8,
            )
        )
        ax.add_patch(
            Rectangle(
                (x - 0.10, y - 0.08), 0.008, 0.16, transform=ax.transAxes, facecolor=color, lw=0
            )
        )
        ax.text(
            x,
            y,
            module,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            weight="bold",
            color="#111827",
        )
    ax.set_title("Declared cross-layer contracts", loc="left", pad=15)
    add_figure_note(
        fig,
        "Architecture schematic: arrows name declared payloads, not measured biological causation.\nThe reduced orchestrator does not execute every declared feedback route.",
        y=0.025,
    )
    fig.tight_layout(rect=(0, 0.10, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _scale_ladder(path: Path) -> Path:
    rows = (
        ("BeeBody", "milliseconds", "joints, wings, sensors"),
        ("BeeBrain", "10–100 ms", "AL / MB / CX abstractions"),
        ("BeeMind", "0.1–1 s", "beliefs and policies"),
        ("BeeSwarm", "seconds–minutes", "dance, fields, tasks"),
        ("BeeNiche", "minutes–days", "comb, heat, landscape"),
    )
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    ax.axis("off")
    for x, header in (
        (0.08, "Module"),
        (0.37, "Conceptual time scale"),
        (0.66, "Represented processes"),
    ):
        ax.text(x, 0.90, header, transform=ax.transAxes, fontsize=10, weight="bold")
    for index, (module, timescale, substrate) in enumerate(rows):
        y = 0.78 - index * 0.14
        ax.add_patch(
            Rectangle(
                (0.06, y - 0.05),
                0.89,
                0.10,
                transform=ax.transAxes,
                facecolor="#F8FAFC",
                edgecolor="#E2E8F0",
                lw=0.7,
            )
        )
        ax.add_patch(
            Rectangle(
                (0.06, y - 0.05),
                0.008,
                0.10,
                transform=ax.transAxes,
                facecolor=module_color(module),
                lw=0,
            )
        )
        for x, text in ((0.08, module), (0.37, timescale), (0.66, substrate)):
            ax.text(
                x,
                y,
                text,
                transform=ax.transAxes,
                va="center",
                fontsize=10,
                color="#111827",
                weight="bold" if x == 0.08 else "normal",
            )
    ax.set_title("Conceptual biological scales — not executed timing", loc="left", pad=15)
    add_figure_note(
        fig,
        "Illustrative process ranges only; rows are not a common clock or a benchmark.\nExecuted control ticks and configured rates belong to the run records/configuration.",
        y=0.025,
    )
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _evidence_ladder(path: Path) -> Path:
    rows = (
        (
            "Scene / contact",
            "FlyBody + MuJoCo",
            "Pose/contact telemetry",
            "Not forward-dynamics calibration",
            "BeeBody",
        ),
        (
            "Source / structure",
            "BeeBrain registry",
            "Source and parser status",
            "Not empirical neural dynamics",
            "BeeBrain",
        ),
        (
            "Reduced kernels",
            "Mind / swarm / niche",
            "Computed diagnostic traces",
            "Not biological validation",
            "BeeMind",
        ),
        (
            "Adapter contracts",
            "BEEHAVE / Hiveopolis",
            "Mapped summary fields",
            "Not external simulator parity",
            "BeeSwarm",
        ),
        (
            "Digital-twin target",
            "Readiness requirements",
            "Assimilation / residual gaps",
            "Not a ready digital twin",
            "BeeNiche",
        ),
    )
    fig, ax = plt.subplots(figsize=(12.0, 5.9))
    ax.axis("off")
    columns = (
        (0.065, "Evidence class", 22),
        (0.285, "Source / backend", 23),
        (0.515, "Potential evidence surface", 26),
        (0.765, "Claim boundary", 27),
    )
    for x, header, _ in columns:
        ax.text(x, 0.90, header, transform=ax.transAxes, fontsize=10, weight="bold")
    for index, (*values, module) in enumerate(rows):
        y = 0.78 - index * 0.145
        ax.add_patch(
            Rectangle(
                (0.045, y - 0.057),
                0.92,
                0.114,
                transform=ax.transAxes,
                facecolor="#F8FAFC",
                edgecolor="#E2E8F0",
                lw=0.7,
            )
        )
        ax.add_patch(
            Rectangle(
                (0.045, y - 0.057),
                0.008,
                0.114,
                transform=ax.transAxes,
                facecolor=module_color(module),
                lw=0,
            )
        )
        for value, (x, _, width) in zip(values, columns, strict=True):
            ax.text(
                x,
                y,
                wrap_label(value, width=width),
                transform=ax.transAxes,
                va="center",
                fontsize=9.3,
                color="#111827",
                weight="bold" if x == 0.065 else "normal",
            )
    ax.set_title("Evidence classes and claim ceilings", loc="left", pad=15)
    add_figure_note(
        fig,
        "Conceptual evidence guide, not an availability report or a ranking of validation.\nRead each artifact’s current sidecar and source record before making an evidence claim.",
        y=0.025,
    )
    fig.tight_layout(rect=(0, 0.11, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path
