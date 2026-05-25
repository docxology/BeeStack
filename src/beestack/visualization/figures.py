"""Publication figure builders for BeeStack outputs."""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle, RegularPolygon

from ..source_refresh import verified_source_refresh_ledger
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
            _first_principles_claim_audit(
                fig_dir / "beestack_first_principles_claim_audit.png"
            ),
            _scholarship_evidence_matrix(
                fig_dir / "beestack_scholarship_evidence_matrix.png"
            ),
            _micro_macro_calibration(
                records, fig_dir / "beebody_beeswarm_micro_macro_calibration.png"
            ),
            _brain_mind_anatomy_policy_map(
                fig_dir / "beebrain_beemind_anatomy_policy_map.png"
            ),
            _niche_adapter_map(records, fig_dir / "beeniche_adapter_niche_map.png"),
            _validation_readiness_residuals(
                fig_dir / "beestack_validation_readiness_residuals.png"
            ),
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
        or "first_principles" in filename
        or "scholarship" in filename
        or "micro_macro" in filename
        or "anatomy_policy" in filename
        or "adapter_niche" in filename
        or "validation_readiness" in filename
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
    if "source refresh" in lowered or "bibliography" in lowered:
        return "source ledger"
    if "beehave" in lowered or "adapter" in lowered:
        return "adapter registry"
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
        "first_principles_claim_boundary": "claim boundary",
        "integrated_run_witness": "run witness",
        "contract_coverage_witness": "contract coverage",
        "methods_provenance_diagnostic": "methods provenance",
        "research_scorecard_diagnostic": "research scorecard",
        "reduced_sensitivity_diagnostic": "sensitivity witness",
        "research_evidence_network": "evidence network",
        "empirical_availability_diagnostic": "empirical availability",
        "cross_stack_synthesis_diagnostic": "synthesis diagnostic",
        "scholarship_evidence_matrix": "source matrix",
        "micro_macro_calibration_boundary": "micro/macro boundary",
        "neurocognitive_mapping_diagnostic": "brain/mind map",
        "adapter_boundary_diagnostic": "adapter boundary",
        "validation_readiness_boundary": "validation boundary",
    }
    return labels.get(claim_tier, textwrap.shorten(claim_tier.replace("_", " "), width=24))


def _claim_color(claim_tier: str) -> str:
    lowered = claim_tier.lower()
    if "strict" in lowered or "body" in lowered:
        return module_color("BeeBody")
    if "empirical" in lowered:
        return module_color("BeeBrain")
    if "adapter" in lowered or "niche" in lowered:
        return module_color("BeeNiche")
    if "validation" in lowered or "residual" in lowered:
        return PALETTE[6]
    if "scholarship" in lowered or "source" in lowered:
        return PALETTE[5]
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
        ("replace direct DOI/source verification or add empirical data", "no new empirical data"),
        (
            "calibrate colony-scale recruitment or make small-scene contacts a population model",
            "no colony calibration",
        ),
        (
            "support connectome-scale, calcium-validated, or learned generative dynamics",
            "no learned neural dynamics",
        ),
        (
            "validate full ecology, real-time hive control, or thermodynamic colony dynamics",
            "no hive-control validation",
        ),
        (
            "provide held-out residuals, uncertainty quantification, or digital-twin readiness",
            "residuals still blocked",
        ),
        ("replace absent calcium payloads with synthetic traces", "no synthetic calcium traces"),
        ("make BeeStack digital-twin ready", "not digital-twin ready"),
    )
    for needle, replacement in replacements:
        if cleaned == needle:
            return replacement
    return textwrap.shorten(cleaned, width=32, placeholder="...")


def _first_principles_claim_audit(path: Path) -> Path:
    rows = [
        (
            "Hard constraint",
            "Every present-tense claim needs generated evidence.",
            "tokens, JSON, reports, sidecars",
            "no manuscript-only metrics",
            "#111827",
        ),
        (
            "Hard constraint",
            "Public data can be absent or unparseable.",
            "source registry + blockers",
            "no synthetic empirical traces",
            module_color("BeeBrain"),
        ),
        (
            "Hard constraint",
            "Visual proof is bounded by backend physics.",
            "FlyBody/MuJoCo + sidecars",
            "no calibration by appearance",
            module_color("BeeBody"),
        ),
        (
            "Soft choice",
            "Reduced kernels stay useful when bounded.",
            "finite diagnostics + sweeps",
            "no hidden biological realism",
            module_color("BeeMind"),
        ),
        (
            "Blocked claim",
            "Digital-twin language requires assimilation and residuals.",
            "readiness review",
            "not ready until measured",
            "#C43C39",
        ),
    ]
    fig, ax = plt.subplots(figsize=(12.4, 5.8))
    ax.axis("off")
    columns = (
        ("Constraint class", 0.055),
        ("First-principles statement", 0.235),
        ("Current evidence surface", 0.585),
        ("Manuscript boundary", 0.795),
    )
    for title, x in columns:
        ax.text(
            x,
            0.88,
            title,
            transform=ax.transAxes,
            va="center",
            fontsize=9,
            color="#111827",
            weight="bold",
        )
    for index, (klass, statement, evidence, boundary, color) in enumerate(rows):
        y = 0.765 - index * 0.135
        ax.add_patch(
            Rectangle(
                (0.035, y - 0.048),
                0.93,
                0.096,
                transform=ax.transAxes,
                facecolor="#F8FAFC" if index % 2 == 0 else "#FFFFFF",
                edgecolor="#CBD5E1",
                lw=0.8,
            )
        )
        ax.add_patch(
            Rectangle(
                (0.035, y - 0.048),
                0.012,
                0.096,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor=color,
                lw=0,
            )
        )
        values = (klass, statement, evidence, boundary)
        for value, (_, x) in zip(values, columns, strict=True):
            ax.text(
                x,
                y,
                textwrap.fill(value, width=36 if x == 0.235 else 24),
                transform=ax.transAxes,
                va="center",
                fontsize=8.2,
                color="#111827",
            )
    ax.text(
        0.5,
        0.09,
        "Reading rule: hard constraints are non-negotiable; soft choices can be replaced only by stronger evidence at the same public contracts.",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        color="#334155",
    )
    ax.set_title("BeeStack first-principles claim audit")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _scholarship_evidence_matrix(path: Path) -> Path:
    records = verified_source_refresh_ledger()
    fig_height = max(5.8, 0.42 * len(records) + 2.2)
    fig, ax = plt.subplots(figsize=(13.4, fig_height))
    ax.axis("off")
    columns = (
        ("Source", 0.045),
        ("DOI", 0.265),
        ("Tier", 0.465),
        ("Sections", 0.610),
        ("Figures", 0.735),
        ("Availability", 0.855),
    )
    for title, x in columns:
        ax.text(x, 0.895, title, transform=ax.transAxes, fontsize=9, weight="bold")
    for index, record in enumerate(records):
        y = 0.825 - index * (0.70 / max(1, len(records) - 1))
        color = _claim_color(record.claim_tier)
        ax.add_patch(
            Rectangle(
                (0.025, y - 0.030),
                0.945,
                0.057,
                transform=ax.transAxes,
                facecolor="#F8FAFC" if index % 2 == 0 else "#FFFFFF",
                edgecolor="#CBD5E1",
                lw=0.55,
            )
        )
        ax.add_patch(
            Rectangle(
                (0.456, y - 0.020),
                0.128,
                0.036,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor="#111827",
                lw=0.35,
                alpha=0.92,
            )
        )
        values = (
            textwrap.shorten(record.citation_key, width=28, placeholder="..."),
            textwrap.shorten(record.doi, width=28, placeholder="..."),
            record.claim_tier.replace("_", " "),
            f"{len(record.section_targets)} mapped",
            f"{len(record.figure_targets)} mapped",
            record.availability_status.replace("_", " "),
        )
        for value, (_, x) in zip(values, columns, strict=True):
            ax.text(
                x,
                y,
                textwrap.fill(value, width=23 if x == 0.855 else 19),
                transform=ax.transAxes,
                va="center",
                fontsize=7.2,
                color="white" if x == 0.465 else "#111827",
            )
    badges = (
        f"{len(records)} verified sources",
        "Perplexity discovery only",
        "DOI/source enforced",
        "availability recorded",
    )
    for index, badge in enumerate(badges):
        x = 0.15 + index * 0.185
        ax.add_patch(
            Rectangle(
                (x, 0.075),
                0.155,
                0.044,
                transform=ax.transAxes,
                facecolor="#EEF2FF",
                edgecolor="#A5B4FC",
                lw=0.7,
            )
        )
        ax.text(
            x + 0.0775,
            0.097,
            badge,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=7.0,
            color="#312E81",
            weight="bold",
        )
    ax.text(
        0.5,
        0.035,
        "Reading rule: a source enters manuscript claims only after direct DOI/source verification.",
        transform=ax.transAxes,
        ha="center",
        fontsize=8.6,
        color="#334155",
    )
    ax.set_title("BeeStack scholarship evidence matrix")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


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
