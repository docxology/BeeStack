"""BeeStack publication figure builders — submodule."""

from __future__ import annotations

import textwrap
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from ..source_refresh import verified_source_refresh_ledger
from .figure_registry import all_figure_narratives
from .style import PALETTE, add_figure_note, module_color, status_color, wrap_label


def _manuscript_figure_claim_map(path: Path) -> Path:
    narratives = [
        narrative for narrative in all_figure_narratives() if narrative.priority == "primary"
    ]
    rows = sorted(narratives, key=lambda item: (item.manuscript_section, item.artifact_path))
    section_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for narrative in rows:
        section = Path(narrative.manuscript_section).name.removesuffix(".md")
        section_counts[section][_claim_family(narrative.claim_tier)] += 1
    sections = sorted(section_counts)
    families = ("empirical", "strict render", "methods", "source", "synthesis", "boundary")
    matrix = [[section_counts[section][family] for family in families] for section in sections]
    fig, ax = plt.subplots(figsize=(10.8, 6.2))
    image = ax.imshow(matrix, cmap="YlGnBu", aspect="auto")
    ax.set_title("BeeStack manuscript figure claim overview", loc="left", pad=14)
    ax.set_xticks(range(len(families)), [wrap_label(family, width=12) for family in families])
    ax.set_yticks(range(len(sections)), [wrap_label(section, width=28) for section in sections])
    ax.tick_params(labelsize=8)
    for row_index, section in enumerate(sections):
        for col_index, family in enumerate(families):
            count = section_counts[section][family]
            ax.text(
                col_index,
                row_index,
                str(count) if count else "-",
                ha="center",
                va="center",
                fontsize=8,
                color="#111827",
                fontweight="bold" if count else "normal",
            )
    ax.set_xlabel("Registered claim family")
    ax.set_ylabel("Manuscript section")
    fig.colorbar(image, ax=ax, label="primary figure count", fraction=0.045, pad=0.02)
    ax.text(
        0.02,
        -0.22,
        (
            f"{len(rows)} primary figure artifacts are grouped here; the split companion "
            "figure lists source classes and unsupported-inference boundaries."
        ),
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        color="#475569",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _manuscript_figure_claim_detail(path: Path) -> Path:
    narratives = [
        narrative for narrative in all_figure_narratives() if narrative.priority == "primary"
    ]
    rows = sorted(narratives, key=lambda item: (item.manuscript_section, item.artifact_path))
    fig, ax = plt.subplots(figsize=(15.0, 11.2))
    ax.axis("off")
    source_class_count = len({_source_class(narrative.source_data) for narrative in rows})
    provenance_badges = (
        f"{len(rows)} primary figures",
        f"{source_class_count} source classes",
        "split-detail view",
        "source and boundary",
    )
    for index, badge in enumerate(provenance_badges):
        x = 0.08 + index * 0.20
        ax.add_patch(
            Rectangle(
                (x, 0.905),
                0.17,
                0.036,
                transform=ax.transAxes,
                facecolor="#F8FAFC",
                edgecolor="#CBD5E1",
                lw=0.7,
            )
        )
        ax.text(
            x + 0.085,
            0.923,
            badge,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=7.4,
            color="#334155",
            weight="bold",
        )
    ax.text(
        0.03,
        0.965,
        "BeeStack manuscript figure claim detail",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=14,
        fontweight="bold",
        color="#111827",
    )
    split = (len(rows) + 1) // 2
    for column_index, column_rows in enumerate((rows[:split], rows[split:])):
        x0 = 0.025 + column_index * 0.49
        ax.text(x0, 0.855, "Section", transform=ax.transAxes, fontsize=8.6, weight="bold")
        ax.text(
            x0 + 0.090,
            0.855,
            "Figure and source",
            transform=ax.transAxes,
            fontsize=8.6,
            weight="bold",
        )
        ax.text(x0 + 0.275, 0.855, "Tier", transform=ax.transAxes, fontsize=8.6, weight="bold")
        ax.text(x0 + 0.355, 0.855, "Boundary", transform=ax.transAxes, fontsize=8.6, weight="bold")
        for index, narrative in enumerate(column_rows):
            y = 0.812 - index * 0.033
            color = _claim_color(narrative.claim_tier)
            facecolor = "#F8FAFC" if index % 2 == 0 else "#FFFFFF"
            ax.add_patch(
                Rectangle(
                    (x0 - 0.006, y - 0.014),
                    0.470,
                    0.028,
                    transform=ax.transAxes,
                    facecolor=facecolor,
                    edgecolor="#E2E8F0",
                    lw=0.45,
                )
            )
            ax.text(
                x0,
                y,
                Path(narrative.manuscript_section).name.replace(".md", ""),
                transform=ax.transAxes,
                va="center",
                fontsize=6.7,
                color="#334155",
            )
            ax.text(
                x0 + 0.090,
                y,
                _figure_source_cell(narrative.artifact_path, narrative.source_data),
                transform=ax.transAxes,
                va="center",
                fontsize=6.5,
                color="#111827",
            )
            ax.add_patch(
                Rectangle(
                    (x0 + 0.275, y - 0.010),
                    0.016,
                    0.020,
                    transform=ax.transAxes,
                    facecolor=color,
                    edgecolor="#111827",
                    lw=0.35,
                )
            )
            ax.text(
                x0 + 0.295,
                y,
                wrap_label(_claim_label(narrative.claim_tier), width=15, max_lines=2),
                transform=ax.transAxes,
                va="center",
                fontsize=6.3,
                color="#111827",
            )
            ax.text(
                x0 + 0.355,
                y,
                wrap_label(
                    _validation_boundary(narrative.unsupported_inference),
                    width=31,
                    max_lines=2,
                ),
                transform=ax.transAxes,
                va="center",
                fontsize=6.3,
                color="#334155",
            )
    legend = (
        ("empirical availability", module_color("BeeBrain")),
        ("strict scene / body", module_color("BeeBody")),
        ("source / synthesis", PALETTE[5]),
        ("blocked or residual", PALETTE[6]),
        ("sidecar pass", status_color("available")),
    )
    for index, (label, color) in enumerate(legend):
        x = 0.08 + index * 0.18
        ax.add_patch(
            Rectangle(
                (x, 0.030),
                0.020,
                0.020,
                transform=ax.transAxes,
                facecolor=color,
                edgecolor="#111827",
                lw=0.35,
            )
        )
        ax.text(
            x + 0.028,
            0.040,
            label,
            transform=ax.transAxes,
            ha="left",
            va="center",
            fontsize=7.4,
            color="#334155",
        )
    add_figure_note(
        fig,
        "Reading rule: this split detail lists provenance and boundaries; the companion overview shows section-level distribution.",
        y=0.006,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _claim_family(claim_tier: str) -> str:
    lowered = claim_tier.lower()
    if "empirical" in lowered or "connectome" in lowered or "structural" in lowered:
        return "empirical"
    if "strict" in lowered or "flybody" in lowered or "scene" in lowered:
        return "strict render"
    if "methods" in lowered or "kernel" in lowered or "coverage" in lowered:
        return "methods"
    if "source" in lowered or "scholarship" in lowered or "provenance" in lowered:
        return "source"
    if "synthesis" in lowered or "research" in lowered:
        return "synthesis"
    return "boundary"


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


def _figure_source_cell(artifact_path: str, source_data: str) -> str:
    figure = _figure_label(artifact_path)
    source = _source_class(source_data)
    return f"{wrap_label(figure, width=24, max_lines=1)}\n[{source}]"


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
