"""Calibration boundaries and conceptual workflow diagrams."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

from .figures_common import _numeric_series
from .style import add_figure_note, module_color, wrap_label


def _micro_macro_calibration(records: list[dict[str, Any]], path: Path) -> Path:
    recruited = _numeric_series(records, "recruited_followers")
    pheromone = _numeric_series(records, "mean_pheromone")
    mean_recruited = float(np.mean(recruited))
    mean_pheromone = float(np.mean(pheromone))
    surfaces = (
        (
            "Separate scene interface",
            "Scripted pose / contact telemetry\nNo scene payload supplied here",
            "BeeBody",
        ),
        (
            "Scholarly anchors",
            "Flight, dance and follower studies\nNo empirical tracks supplied here",
            "BeeBrain",
        ),
        (
            "Supplied reduced-run records",
            f"Mean followers: {mean_recruited:.1f}\nMean pheromone: {mean_pheromone:.2f} a.u.",
            "BeeSwarm",
        ),
    )
    fig, ax = plt.subplots(figsize=(11.6, 5.6))
    ax.axis("off")
    for index, (title, detail, module) in enumerate(surfaces):
        x = 0.04 + index * 0.325
        color = module_color(module)
        ax.add_patch(
            Rectangle(
                (x, 0.48),
                0.29,
                0.34,
                transform=ax.transAxes,
                facecolor="#F8FAFC",
                edgecolor="#CBD5E1",
                lw=0.8,
            )
        )
        ax.add_patch(
            Rectangle((x, 0.48), 0.008, 0.34, transform=ax.transAxes, facecolor=color, lw=0)
        )
        ax.text(
            x + 0.02,
            0.75,
            wrap_label(title, width=26),
            transform=ax.transAxes,
            fontsize=11,
            weight="bold",
            va="center",
            color="#111827",
        )
        ax.text(
            x + 0.02,
            0.60,
            detail,
            transform=ax.transAxes,
            fontsize=9.2,
            va="center",
            color="#334155",
            linespacing=1.6,
        )
    ax.text(
        0.04,
        0.34,
        "Calibration is a separate, unfulfilled evidence requirement",
        transform=ax.transAxes,
        fontsize=11,
        weight="bold",
        color="#991B1B",
    )
    requirements = (
        "Matched observables + units",
        "Held-out recruitment residuals",
        "Uncertainty + external colony data",
    )
    for index, text in enumerate(requirements):
        ax.text(
            0.04 + index * 0.325,
            0.22,
            wrap_label(text, width=27),
            transform=ax.transAxes,
            fontsize=10,
            va="center",
            color="#334155",
        )
    ax.set_title("Micro-to-macro comparison is not calibration", loc="left", pad=15)
    add_figure_note(
        fig,
        "Independent evidence surfaces: no causal or fitted micro → colony transfer is demonstrated.\nDisplayed means are computed only from the supplied reduced-run records.",
        y=0.025,
    )
    fig.tight_layout(rect=(0, 0.10, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _brain_mind_anatomy_policy_map(path: Path) -> Path:
    rows = (
        ("Antennal lobe", "Odor representation", "Observation likelihood"),
        ("Mushroom body", "Learning / memory", "Preferences + expected value"),
        ("Central complex", "Orientation / action", "Policy transition terms"),
        ("Waggle followers", "Spatial information", "Contextual policy prior"),
    )
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    ax.axis("off")
    columns = (
        (0.06, "Scholarly anchor", 24),
        (0.37, "Conceptual role", 25),
        (0.70, "Controller analogy", 27),
    )
    for x, title, _ in columns:
        ax.text(x, 0.89, title, transform=ax.transAxes, fontsize=10, weight="bold")
    for index, row in enumerate(rows):
        y = 0.76 - index * 0.16
        for value, (x, _, width) in zip(row, columns, strict=True):
            ax.text(
                x,
                y,
                wrap_label(value, width=width),
                transform=ax.transAxes,
                va="center",
                fontsize=10,
                color="#111827",
            )
        ax.plot([0.05, 0.95], [y - 0.065] * 2, transform=ax.transAxes, color="#E2E8F0", lw=0.8)
        for start, end in ((0.285, 0.345), (0.615, 0.675)):
            ax.add_patch(
                FancyArrowPatch(
                    (start, y),
                    (end, y),
                    transform=ax.transAxes,
                    arrowstyle="-",
                    linestyle="--",
                    color="#64748B",
                    lw=1.2,
                )
            )
    ax.set_title("Anatomy and policy: conceptual analogies only", loc="left", pad=15)
    add_figure_note(
        fig,
        "Dashed links denote analogy, not fitted anatomy → policy mappings or executed neural feedback.\nNo connectome assimilation, calcium validation, or learned generative controller is established.",
        y=0.025,
    )
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _niche_adapter_map(records: list[dict[str, Any]], path: Path) -> Path:
    comb = _numeric_series(records, "comb_fraction")
    thermal = _numeric_series(records, "brood_temperature_error_c")
    final_comb = comb[-1]
    max_thermal = max(abs(value) for value in thermal)
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.5), gridspec_kw={"width_ratios": [1, 1.5]})
    for ax in axes:
        ax.axis("off")
    axes[0].set_title("Supplied run witnesses", loc="left", pad=15)
    for index, (label, value) in enumerate(
        (
            ("Final comb fraction", f"{final_comb:.2f}"),
            ("Maximum absolute thermal error", f"{max_thermal:.2f} °C"),
        )
    ):
        y = 0.73 - index * 0.37
        axes[0].text(
            0.03, y, value, transform=axes[0].transAxes, fontsize=23, weight="bold", color="#111827"
        )
        axes[0].text(
            0.03,
            y - 0.12,
            wrap_label(label, width=29),
            transform=axes[0].transAxes,
            fontsize=10,
            color="#334155",
            va="center",
        )
    axes[1].set_title("Adapter schema (conceptual)", loc="left", pad=15)
    fields = (
        ("CombGrid + configuration", "Comb / thermal / forage summaries", module_color("BeeNiche")),
        (
            "BEEHAVE-compatible fields",
            "Resource proxy; not simulator parity",
            module_color("BeeSwarm"),
        ),
        (
            "Hiveopolis-compatible fields",
            "Thermal band / target; not live control",
            module_color("BeeMind"),
        ),
    )
    for index, (title, detail, color) in enumerate(fields):
        y = 0.81 - index * 0.30
        axes[1].add_patch(
            Rectangle(
                (0.04, y - 0.10),
                0.92,
                0.20,
                transform=axes[1].transAxes,
                facecolor="#F8FAFC",
                edgecolor=color,
                lw=1.1,
            )
        )
        axes[1].text(
            0.07,
            y + 0.027,
            title,
            transform=axes[1].transAxes,
            fontsize=10.5,
            weight="bold",
            color="#111827",
            va="center",
        )
        axes[1].text(
            0.07,
            y - 0.045,
            detail,
            transform=axes[1].transAxes,
            fontsize=9,
            color="#334155",
            va="center",
        )
    add_figure_note(
        fig,
        "Left: reduced telemetry only. Right: NicheAdapterSummary field groups; no adapter payload is supplied.\nCompatible names and units do not validate full ecology, thermodynamics, or real-time hive control.",
        y=0.025,
    )
    fig.tight_layout(rect=(0, 0.13, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _validation_readiness_residuals(path: Path) -> Path:
    rows = (
        ("Local contract", "Verification commands", "Inspect current check receipts"),
        ("Local contract", "Figure sidecars", "Caption + provenance metadata"),
        ("Local contract", "Source audit", "DOI / source verification"),
        ("Local contract", "Availability records", "Missing payloads remain explicit"),
        ("Not supplied", "Held-out residuals", "Requires external validation data"),
        ("Not supplied", "Uncertainty quantification", "Requires predictive intervals"),
        ("Not supplied", "Longitudinal assimilation", "Requires colony time-series data"),
        ("Not supplied", "Digital-twin governance", "Requires readiness evidence"),
    )
    fig, ax = plt.subplots(figsize=(10.8, 6.2))
    ax.axis("off")
    for x, title in ((0.06, "Evidence role"), (0.28, "Requirement"), (0.61, "Interpretation")):
        ax.text(x, 0.91, title, transform=ax.transAxes, fontsize=10, weight="bold")
    for index, (status, item, interpretation) in enumerate(rows):
        y = 0.81 - index * 0.092
        ax.add_patch(
            Rectangle(
                (0.04, y - 0.037),
                0.92,
                0.074,
                transform=ax.transAxes,
                facecolor="#F8FAFC",
                edgecolor="#E2E8F0",
                lw=0.6,
            )
        )
        for x, value in ((0.06, status), (0.28, item), (0.61, interpretation)):
            ax.text(
                x,
                y,
                value,
                transform=ax.transAxes,
                fontsize=9.4,
                va="center",
                color="#991B1B" if x == 0.06 and status == "Not supplied" else "#111827",
            )
    ax.set_title("Validation requirements — no residual data supplied", loc="left", pad=15)
    add_figure_note(
        fig,
        "Conceptual readiness checklist, not a report that local checks passed.\nNo residual bars or predictive intervals are drawn without their underlying data.",
        y=0.025,
    )
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _pipeline_overview(path: Path) -> Path:
    stages = (
        ("Configure", "Project configuration", "BeeNiche"),
        ("Compute", "Reduced run + gated analyses", "BeeMind"),
        ("Write artifacts", "Records, figures, reports", "BeeBrain"),
        ("Audit / release", "Check receipts + manuscript", "BeeBody"),
    )
    fig, ax = plt.subplots(figsize=(11.2, 4.7))
    ax.axis("off")
    for index, (title, detail, module) in enumerate(stages):
        x = 0.025 + index * 0.25
        ax.add_patch(
            Rectangle(
                (x, 0.50),
                0.205,
                0.28,
                transform=ax.transAxes,
                facecolor="#F8FAFC",
                edgecolor=module_color(module),
                lw=1.4,
            )
        )
        ax.text(
            x + 0.1025,
            0.69,
            title,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=11,
            weight="bold",
            color="#111827",
        )
        ax.text(
            x + 0.1025,
            0.58,
            wrap_label(detail, width=23),
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=9.2,
            color="#334155",
        )
        if index < len(stages) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (x + 0.205, 0.64),
                    (x + 0.248, 0.64),
                    transform=ax.transAxes,
                    arrowstyle="-|>",
                    mutation_scale=13,
                    lw=1.4,
                    color="#475569",
                )
            )
    ax.text(
        0.03,
        0.30,
        "Separate presentation branch",
        transform=ax.transAxes,
        fontsize=10.5,
        weight="bold",
        color="#111827",
    )
    ax.text(
        0.03,
        0.18,
        "FlyBody / MuJoCo pose-contact scenes + animation artifacts",
        transform=ax.transAxes,
        fontsize=10,
        color="#334155",
    )
    ax.set_title("Research artifact workflow (conceptual)", loc="left", pad=15)
    add_figure_note(
        fig,
        "Workflow order is not a current execution receipt. Empirical analysis remains payload-gated.\nAnimation/contact artifacts do not substitute for calibrated forward dynamics or biological validation.",
        y=0.025,
    )
    fig.tight_layout(rect=(0, 0.13, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path
