"""Publication figure builders for BeeStack outputs."""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle, RegularPolygon

from .figure_metadata import write_figure_sidecar
from .figure_registry import all_figure_narratives
from .style import PALETTE, apply_panel_style, module_color, style_context


def generate_analysis_figures(
    records: list[dict[str, Any]], module_names: list[str], fig_dir: Path
) -> list[Path]:
    """Generate deterministic module diagnostics and whole-stack abstracts."""

    fig_dir.mkdir(parents=True, exist_ok=True)
    with style_context():
        paths = [
            _energy_timeseries(records, fig_dir / "body_energy_timeseries.png"),
            _comb_timeseries(records, fig_dir / "comb_fraction_timeseries.png"),
            _module_coverage(module_names, fig_dir / "module_contract_coverage.png"),
            _body_motion_power_phase(records, fig_dir / "beebody_motion_power_phase.png"),
            _brain_empirical_alignment(
                records, fig_dir / "beebrain_empirical_alignment_timeseries.png"
            ),
            _mind_policy_timeline(records, fig_dir / "beemind_policy_timeline.png"),
            _swarm_recruitment_allocation(
                records, fig_dir / "beeswarm_recruitment_task_allocation.png"
            ),
            _niche_thermal_comb_panel(records, fig_dir / "beeniche_thermal_comb_panel.png"),
            _stack_graphical_abstract(module_names, fig_dir / "beestack_graphical_abstract.png"),
            _contract_network(fig_dir / "beestack_contract_network.png"),
            _scale_ladder(fig_dir / "beestack_scale_ladder.png"),
            _evidence_ladder(fig_dir / "beestack_evidence_ladder.png"),
            _manuscript_figure_claim_map(fig_dir / "manuscript_figure_claim_map.png"),
            _pipeline_overview(fig_dir / "beestack_pipeline_overview.png"),
        ]
    primary_figure_count = sum(
        1 for narrative in all_figure_narratives() if narrative.priority == "primary"
    )
    for path in paths:
        metrics = (
            {"primary_figure_count": primary_figure_count}
            if path.name == "manuscript_figure_claim_map.png"
            else None
        )
        write_figure_sidecar(
            path,
            title=path.stem.replace("_", " ").title(),
            backend="Matplotlib",
            fidelity=_analysis_figure_fidelity(path.name),
            source_data="output/data/simulation_records.json and module coverage records",
            validation_status="nonblank quality sidecar generated",
            regeneration_command="uv run python scripts/analysis_pipeline.py",
            metrics=metrics,
        )
    return paths


def _analysis_figure_fidelity(filename: str) -> str:
    """Classify base analysis figures without overstating biological fidelity."""

    if "beebrain_empirical" in filename:
        return "empirical summary projected into a reduced BeeBrain contract"
    if (
        "graphical_abstract" in filename
        or "contract" in filename
        or "pipeline" in filename
        or "evidence_ladder" in filename
        or "claim_map" in filename
    ):
        return "architecture schematic"
    return "reduced deterministic kernel diagnostic"


def _steps(records: list[dict[str, Any]]) -> list[int]:
    if not records:
        return [0]
    return [int(row.get("step_index", index)) for index, row in enumerate(records)]


def _numeric_series(records: list[dict[str, Any]], key: str, default: float = 0.0) -> list[float]:
    if not records:
        return [default]
    return [float(row.get(key, default)) for row in records]


def _policy_series(records: list[dict[str, Any]]) -> tuple[list[str], list[int]]:
    policies = [str(row.get("selected_policy", "unassigned")) for row in records] or ["unassigned"]
    order = {policy: index for index, policy in enumerate(dict.fromkeys(policies))}
    return policies, [order[policy] for policy in policies]


def _energy_timeseries(records: list[dict[str, Any]], path: Path) -> Path:
    steps = _steps(records)
    energy = _numeric_series(records, "energy_j")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(steps, energy, marker="o", color="#0f766e", label="Energy (J)")
    ax.set_xlabel("Control step")
    ax.set_ylabel("Energy (J)")
    ax.set_title("BeeBody energy across integrated BeeStack run")
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
    ax.plot(steps, alignment, marker="o", color="#1d4ed8", lw=2)
    ax.fill_between(steps, alignment, color="#bfdbfe", alpha=0.45)
    if odors[-1]:
        ax.text(steps[-1], alignment[-1], f" {odors[-1]}", va="center", fontsize=8)
    ax.set_ylim(0, max(1.0, max(alignment) * 1.15))
    ax.set_xlabel("Control step")
    ax.set_ylabel("Template alignment")
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
    ax2.plot(steps, pheromone, color="#0f766e", marker="o", label="Mean pheromone")
    ax2.set_ylabel("Mean pheromone")
    ax.set_title("BeeSwarm recruitment and shared-field state")
    ax.bar_label(bars, fmt="%.0f", fontsize=7, padding=2)
    apply_panel_style(ax, grid_axis="y")
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
    ax2.plot(steps, error, color="#dc2626", marker="o", label="Brood temp error")
    ax2.set_ylabel("Brood temperature error (C)")
    ax.set_title("BeeNiche comb and brood-thermal diagnostics")
    apply_panel_style(ax, grid_axis="both")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _stack_graphical_abstract(module_names: list[str], path: Path) -> Path:
    modules = module_names or ["BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"]
    captions = {
        "BeeBody": "FlyBody MJCF\nsensing + actuation",
        "BeeBrain": "AL/MB/CX\nempirical drives",
        "BeeMind": "beliefs\npolicy choice",
        "BeeSwarm": "dance + pheromone\ncolony allocation",
        "BeeNiche": "comb + thermal\nforaging context",
    }
    colors = [module_color(module) for module in modules]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.axis("off")
    x_positions = np.linspace(0.08, 0.92, len(modules))
    y = 0.55
    for index, (module, x) in enumerate(zip(modules, x_positions, strict=False)):
        ax.add_patch(
            RegularPolygon(
                (x, y),
                numVertices=6,
                radius=0.092,
                orientation=np.pi / 6,
                transform=ax.transAxes,
                facecolor=colors[index % len(colors)],
                edgecolor="#111827",
                lw=1.2,
                alpha=0.9,
            )
        )
        ax.text(x, y + 0.135, module, transform=ax.transAxes, ha="center", fontsize=11)
        ax.text(
            x,
            y - 0.005,
            captions.get(module, "typed\nmodule"),
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=8,
            color="white",
        )
        if index < len(modules) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (x + 0.088, y),
                    (x_positions[index + 1] - 0.088, y),
                    transform=ax.transAxes,
                    arrowstyle="->",
                    mutation_scale=14,
                    lw=1.4,
                    color="#334155",
                )
            )
    ax.text(
        0.5,
        0.14,
        "Observation -> BrainState -> BeliefState -> BeeAgent/PheromoneField -> CombGrid",
        transform=ax.transAxes,
        ha="center",
        fontsize=10,
    )
    ax.set_title("BeeStack graphical abstract: body-first honeybee evidence-typed scaffold")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


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


def _manuscript_figure_claim_map(path: Path) -> Path:
    narratives = [
        narrative for narrative in all_figure_narratives() if narrative.priority == "primary"
    ]
    rows = sorted(narratives, key=lambda item: (item.manuscript_section, item.artifact_path))
    fig_height = max(7.0, 0.56 * len(rows) + 1.8)
    fig, ax = plt.subplots(figsize=(13.2, fig_height))
    ax.axis("off")
    source_class_count = len({_source_class(narrative.source_data) for narrative in rows})
    provenance_badges = (
        f"{len(rows)} primary figures",
        f"{source_class_count} source classes",
        "sidecar-validated",
        "gap-bounded",
    )
    for index, badge in enumerate(provenance_badges):
        x = 0.145 + index * 0.18
        ax.add_patch(
            Rectangle(
                (x, 0.932),
                0.15,
                0.035,
                transform=ax.transAxes,
                facecolor="#F1F5F9",
                edgecolor="#CBD5E1",
                lw=0.7,
            )
        )
        ax.text(
            x + 0.075,
            0.949,
            badge,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=7.4,
            color="#334155",
            weight="bold",
        )
    columns = (
        ("Manuscript section", 0.035),
        ("Figure", 0.205),
        ("Claim tier", 0.410),
        ("Source class", 0.600),
        ("Validation / boundary", 0.745),
    )
    for header, x in columns:
        ax.text(
            x,
            0.895,
            header,
            transform=ax.transAxes,
            va="center",
            fontsize=9,
            color="#111827",
            weight="bold",
        )
    for index, narrative in enumerate(rows):
        y = 0.835 - index * (0.70 / max(1, len(rows) - 1))
        color = _claim_color(narrative.claim_tier)
        ax.add_patch(
            Rectangle(
                (0.02, y - 0.029),
                0.95,
                0.055,
                transform=ax.transAxes,
                facecolor="#F8FAFC" if index % 2 == 0 else "#FFFFFF",
                edgecolor="#CBD5E1",
                lw=0.5,
            )
        )
        ax.add_patch(
            Rectangle(
                (0.400, y - 0.020),
                0.18,
                0.036,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor="#111827",
                lw=0.35,
                alpha=0.92,
            )
        )
        values = (
            Path(narrative.manuscript_section).name.replace(".md", ""),
            _figure_label(narrative.artifact_path),
            _claim_label(narrative.claim_tier),
            _source_class(narrative.source_data),
            _validation_boundary(narrative.unsupported_inference),
        )
        for value, (_, x) in zip(values, columns, strict=True):
            ax.text(
                x,
                y,
                value,
                transform=ax.transAxes,
                va="center",
                fontsize=7.2 if x == 0.745 else 7.7,
                color="white" if x == 0.410 else "#111827",
                clip_on=True,
            )
    ax.text(
        0.5,
        0.04,
        "Reading rule: manuscript figures are evidence artifacts only at their registered claim tier.",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        color="#334155",
    )
    ax.set_title("BeeStack manuscript figure claim map")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _source_class(source_data: str) -> str:
    lowered = source_data.lower()
    if "empirical" in lowered or "brain_data" in lowered:
        return "empirical registry"
    if "methods" in lowered:
        return "methods analysis"
    if "synthesis" in lowered or "research" in lowered:
        return "research synthesis"
    if "simulation" in lowered or "records" in lowered:
        return "simulation records"
    return "registry/index"


def _figure_label(artifact_path: str) -> str:
    label = Path(artifact_path).stem.replace("_", " ")
    return textwrap.shorten(label, width=31, placeholder="...")


def _claim_label(claim_tier: str) -> str:
    labels = {
        "architecture_schematic": "architecture",
        "strict_visual_plus_reduced_telemetry": "strict + telemetry",
        "empirical_reduced_or_availability": "empirical availability",
        "empirical_reduced_or_availability_gated": "empirical availability",
        "reduced_validated_kernel": "reduced kernel",
        "strict_small_scene_not_colony_dynamics": "strict scene only",
        "fidelity_boundary": "fidelity boundary",
        "manuscript_figure_provenance_map": "figure provenance",
        "empirical_availability_diagnostic": "empirical availability",
        "cross_stack_synthesis_diagnostic": "synthesis diagnostic",
    }
    return labels.get(claim_tier, textwrap.shorten(claim_tier.replace("_", " "), width=24))


def _claim_color(claim_tier: str) -> str:
    lowered = claim_tier.lower()
    if "strict" in lowered or "body" in lowered:
        return module_color("BeeBody")
    if "empirical" in lowered:
        return module_color("BeeBrain")
    if "synthesis" in lowered or "map" in lowered:
        return PALETTE[5]
    if "blocked" in lowered or "digital" in lowered:
        return PALETTE[6]
    return module_color("BeeMind")


def _validation_boundary(unsupported_inference: str) -> str:
    return f"sidecar pass; {_short_boundary(unsupported_inference)}"


def _short_boundary(text: str) -> str:
    cleaned = text.removeprefix("Does not ").removeprefix("does not ").rstrip(".")
    replacements = (
        (
            "support a claim of biological or digital-twin validation",
            "no bio/digital-twin validation",
        ),
        ("calibrate honeybee biomechanics or aerodynamics", "no biomechanics calibration"),
        (
            "support connectome-scale or calcium-validated dynamics",
            "no calcium/connectome validation",
        ),
        (
            "support a learned or biologically calibrated generative controller",
            "no learned controller claim",
        ),
        (
            "support a learned or biologically calibrated generative model",
            "no learned model claim",
        ),
        ("validate colony-scale recruitment dynamics", "no colony recruitment validation"),
        ("support a full ecology or hive thermodynamics engine", "no full ecology engine"),
        ("remove the assimilation, residual, uncertainty, or governance gaps", "gaps remain"),
        (
            "add empirical evidence beyond the registered figure sidecars",
            "no added empirical evidence",
        ),
        (
            "support a complete multimodal empirical assimilation pipeline",
            "no full assimilation",
        ),
        ("replace absent calcium payloads with synthetic traces", "no synthetic calcium traces"),
        ("make BeeStack digital-twin ready", "not digital-twin ready"),
    )
    for needle, replacement in replacements:
        if cleaned == needle:
            return replacement
    return textwrap.shorten(cleaned, width=32, placeholder="...")


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
