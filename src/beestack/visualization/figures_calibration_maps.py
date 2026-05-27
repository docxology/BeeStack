"""BeeStack publication figure builders — submodule."""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

from .figures_common import (
    _numeric_series,
)
from .style import PALETTE, module_color


def _micro_macro_calibration(records: list[dict[str, Any]], path: Path) -> Path:
    recruited = _numeric_series(records, "recruited_followers")
    pheromone = _numeric_series(records, "mean_pheromone")
    mean_recruited = float(np.mean(recruited))
    mean_pheromone = float(np.mean(pheromone))
    blocks = [
        (
            "Strict micro scene",
            "FlyBody/MuJoCo body plan\ncontact metrics\nrender sidecars",
            module_color("BeeBody"),
        ),
        (
            "Waggle evidence anchors",
            "Riley flight paths\nLandgraf dance motion\nfollower neuroethology",
            "#0F766E",
        ),
        (
            "Reduced macro summaries",
            f"BeeSwarm followers mean {mean_recruited:.1f}\n"
            f"pheromone mean {mean_pheromone:.2f}\nBEEHAVE-compatible fields",
            module_color("BeeSwarm"),
        ),
        (
            "Blocked calibration",
            "no held-out recruitment residuals\nno colony-scale fit\nno causal validation",
            "#C43C39",
        ),
    ]
    fig, ax = plt.subplots(figsize=(12.6, 5.4))
    ax.axis("off")
    x_positions = (0.07, 0.32, 0.57, 0.82)
    for index, ((title, detail, color), x) in enumerate(zip(blocks, x_positions, strict=True)):
        ax.add_patch(
            Rectangle(
                (x, 0.42),
                0.17,
                0.27,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor="#111827",
                lw=1.0,
                alpha=0.92,
            )
        )
        ax.text(
            x + 0.085,
            0.635,
            title,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=9.0,
            color="white",
            weight="bold",
        )
        ax.text(
            x + 0.085,
            0.515,
            detail,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=7.4,
            color="white",
        )
        if index < len(blocks) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (x + 0.17, 0.555),
                    (x_positions[index + 1], 0.555),
                    transform=ax.transAxes,
                    arrowstyle="->",
                    mutation_scale=15,
                    lw=1.4,
                    color="#334155",
                )
            )
    rows = (
        ("Allowed comparison", "schema and units can be mapped across layers"),
        ("Current evidence", "small-scene metrics and deterministic reduced swarm traces"),
        ("Not yet evidence", "external colony calibration, prediction intervals, residual panels"),
    )
    for index, (label, detail) in enumerate(rows):
        y = 0.255 - index * 0.070
        ax.text(0.12, y, label, transform=ax.transAxes, fontsize=8.4, weight="bold")
        ax.text(0.31, y, detail, transform=ax.transAxes, fontsize=8.2, color="#334155")
    ax.set_title("BeeBody to BeeSwarm micro-to-macro calibration boundary")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _brain_mind_anatomy_policy_map(path: Path) -> Path:
    rows = [
        ("Antennal lobe", "odor channels", "Observation likelihood", module_color("BeeBrain")),
        ("Mushroom body", "learning/memory anchor", "Preferences + expected value", "#2563EB"),
        ("Central complex", "orientation/action anchor", "Policy transition terms", "#7C3AED"),
        ("Waggle followers", "spatial-information anchor", "Contextual policy prior", "#0F766E"),
    ]
    fig, ax = plt.subplots(figsize=(12.2, 5.8))
    ax.axis("off")
    headers = ("Scholarly anchor", "Data role", "BeeMind contract")
    for x, header in zip((0.12, 0.43, 0.72), headers, strict=True):
        ax.text(x, 0.84, header, transform=ax.transAxes, fontsize=9.5, weight="bold")
    for index, (anchor, role, contract, color) in enumerate(rows):
        y = 0.72 - index * 0.145
        for x, text, width in (
            (0.08, anchor, 0.20),
            (0.38, role, 0.21),
            (0.68, contract, 0.24),
        ):
            ax.add_patch(
                Rectangle(
                    (x, y - 0.040),
                    width,
                    0.080,
                    transform=ax.transAxes,
                    facecolor=color if x == 0.08 else "#F8FAFC",
                    edgecolor="#CBD5E1",
                    lw=0.8,
                )
            )
            ax.text(
                x + width / 2,
                y,
                textwrap.fill(text, width=23),
                transform=ax.transAxes,
                ha="center",
                va="center",
                fontsize=8.0,
                color="white" if x == 0.08 else "#111827",
                weight="bold" if x == 0.08 else "normal",
            )
        ax.add_patch(
            FancyArrowPatch(
                (0.28, y),
                (0.38, y),
                transform=ax.transAxes,
                arrowstyle="->",
                mutation_scale=11,
                lw=1.0,
                color="#475569",
            )
        )
        ax.add_patch(
            FancyArrowPatch(
                (0.59, y),
                (0.68, y),
                transform=ax.transAxes,
                arrowstyle="->",
                mutation_scale=11,
                lw=1.0,
                color="#475569",
            )
        )
    ax.add_patch(
        Rectangle(
            (0.19, 0.075),
            0.62,
            0.080,
            transform=ax.transAxes,
            facecolor="#FEF2F2",
            edgecolor="#FCA5A5",
            lw=0.8,
        )
    )
    ax.text(
        0.50,
        0.116,
        "Blocked claim: no connectome-scale assimilation, calcium-validated dynamics, or learned generative model.",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=8.4,
        color="#991B1B",
        weight="bold",
    )
    ax.set_title("BeeBrain anatomy-data-to-BeeMind belief-policy mapping")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _niche_adapter_map(records: list[dict[str, Any]], path: Path) -> Path:
    comb = _numeric_series(records, "comb_fraction")
    thermal = _numeric_series(records, "brood_temperature_error_c")
    final_comb = comb[-1]
    max_thermal = max(abs(value) for value in thermal)
    nodes = {
        "CombGrid": (0.50, 0.58, f"comb final {final_comb:.2f}", module_color("BeeNiche")),
        "Thermal field": (0.23, 0.62, f"max error {max_thermal:.2f} C", "#DC2626"),
        "Forage map": (0.23, 0.30, "landscape summaries", "#0F766E"),
        "BEEHAVE adapter": (0.77, 0.62, "colony summaries", "#F59E0B"),
        "Hiveopolis boundary": (0.77, 0.30, "interface target", "#7C3AED"),
    }
    fig, ax = plt.subplots(figsize=(11.4, 5.8))
    ax.axis("off")
    for name, (x, y, detail, color) in nodes.items():
        ax.add_patch(
            Rectangle(
                (x - 0.115, y - 0.065),
                0.23,
                0.13,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor="#111827",
                lw=1.0,
                alpha=0.92,
            )
        )
        ax.text(
            x,
            y + 0.024,
            name,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=9.0,
            color="white",
            weight="bold",
        )
        ax.text(
            x,
            y - 0.030,
            detail,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=7.5,
            color="white",
        )
    arrows = (
        ("Thermal field", "CombGrid", "brood context"),
        ("Forage map", "CombGrid", "resource context"),
        ("CombGrid", "BEEHAVE adapter", "summary fields"),
        ("CombGrid", "Hiveopolis boundary", "not real-time control"),
    )
    for source, target, label in arrows:
        sx, sy, *_ = nodes[source]
        tx, ty, *_ = nodes[target]
        ax.add_patch(
            FancyArrowPatch(
                (sx, sy),
                (tx, ty),
                transform=ax.transAxes,
                arrowstyle="->",
                mutation_scale=13,
                lw=1.2,
                color="#334155",
                shrinkA=52,
                shrinkB=52,
            )
        )
        ax.text(
            (sx + tx) / 2,
            (sy + ty) / 2 + 0.028,
            label,
            transform=ax.transAxes,
            ha="center",
            fontsize=7.1,
            color="#334155",
        )
    ax.text(
        0.5,
        0.105,
        "Reading rule: adapters expose compatible summaries; they are not full ecology or hive-control validation.",
        transform=ax.transAxes,
        ha="center",
        fontsize=8.7,
        color="#334155",
    )
    ax.set_title("BeeNiche BEEHAVE/Hiveopolis adapter and comb-thermal-forage map")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _validation_readiness_residuals(path: Path) -> Path:
    rows = [
        ("Implemented", "uv/pytest/ruff gates", "local verification", "#0F766E"),
        ("Implemented", "figure sidecars", "caption + DOI/source metadata", "#0F766E"),
        ("Implemented", "source audit", "bibliography DOI contract", "#0F766E"),
        ("Implemented", "availability records", "blocked empirical payloads explicit", "#0F766E"),
        ("Blocked", "held-out residuals", "no external validation panel", "#C43C39"),
        ("Blocked", "uncertainty quantification", "no posterior predictive interval", "#C43C39"),
        ("Blocked", "longitudinal assimilation", "no living-colony data stream", "#C43C39"),
        ("Blocked", "digital-twin governance", "readiness target only", "#C43C39"),
    ]
    fig, ax = plt.subplots(figsize=(12.4, 6.0))
    ax.axis("off")
    columns = (("Status", 0.09), ("Evidence or blocker", 0.28), ("Current interpretation", 0.58))
    for header, x in columns:
        ax.text(x, 0.86, header, transform=ax.transAxes, fontsize=9.5, weight="bold")
    for index, (status, item, interpretation, color) in enumerate(rows):
        y = 0.77 - index * 0.078
        ax.add_patch(
            Rectangle(
                (0.055, y - 0.032),
                0.89,
                0.060,
                transform=ax.transAxes,
                facecolor="#F8FAFC" if index % 2 == 0 else "#FFFFFF",
                edgecolor="#CBD5E1",
                lw=0.55,
            )
        )
        ax.add_patch(
            Rectangle(
                (0.080, y - 0.021),
                0.130,
                0.040,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor="#111827",
                lw=0.4,
                alpha=0.92,
            )
        )
        ax.text(
            0.145,
            y,
            status,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=7.6,
            color="white",
            weight="bold",
        )
        ax.text(0.28, y, item, transform=ax.transAxes, va="center", fontsize=8.1)
        ax.text(
            0.58,
            y,
            interpretation,
            transform=ax.transAxes,
            va="center",
            fontsize=8.1,
            color="#334155",
        )
    ax.text(
        0.50,
        0.065,
        "No residual bars are drawn because held-out validation residuals are not yet generated.",
        transform=ax.transAxes,
        ha="center",
        fontsize=8.8,
        color="#991B1B",
        weight="bold",
    )
    ax.set_title("BeeStack validation readiness and explicitly blocked residual evidence")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _pipeline_overview(path: Path) -> Path:
    stages = [
        ("config", "manuscript/config.yaml", PALETTE[5]),
        ("simulate", "analysis_pipeline.py", module_color("BeeNiche")),
        ("render", "generate_animations.py", module_color("BeeBody")),
        ("validate", "pytest + verify", PALETTE[6]),
        ("publish", "reports + manuscript", module_color("BeeBrain")),
    ]
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.axis("off")
    for index, (title, detail, color) in enumerate(stages):
        x = 0.08 + index * 0.21
        ax.add_patch(
            Rectangle(
                (x, 0.42),
                0.15,
                0.18,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor="#111827",
                lw=1.0,
                alpha=0.9,
            )
        )
        ax.text(
            x + 0.075,
            0.535,
            title,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=10,
            color="white",
            weight="bold",
        )
        ax.text(
            x + 0.075,
            0.465,
            detail,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=7,
            color="white",
        )
        if index < len(stages) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (x + 0.15, 0.51),
                    (x + 0.205, 0.51),
                    transform=ax.transAxes,
                    arrowstyle="->",
                    mutation_scale=13,
                    lw=1.4,
                    color="#334155",
                )
            )
    ax.text(
        0.5,
        0.24,
        "outputs: data manifests, analysis figures, BeeBody FlyBody GIFs, swarm behavior GIFs, reports, hydrated manuscript",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
    )
    ax.set_title("BeeStack research-operations pipeline")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path
