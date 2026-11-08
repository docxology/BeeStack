"""BeeStack publication figure builders — submodule."""

from __future__ import annotations

import textwrap
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from ..source_refresh import verified_source_refresh_ledger
from .figure_registry import _claim_family, _primary_figure_source_classes, all_figure_narratives
from .style import PALETTE, add_figure_note, module_color, wrap_label


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
    ax.set_title("Registered primary figures by section", loc="left", pad=14)
    ax.set_xticks(range(len(families)), [wrap_label(family, width=12) for family in families])
    ax.set_yticks(range(len(sections)), [wrap_label(section, width=28) for section in sections])
    ax.tick_params(labelsize=8)
    for row_index, section in enumerate(sections):
        for col_index, family in enumerate(families):
            count = section_counts[section][family]
            ax.text(
                col_index,
                row_index,
                str(count),
                ha="center",
                va="center",
                fontsize=8,
                color="white" if image.norm(count) > 0.55 else "#111827",
                fontweight="bold" if count else "normal",
            )
    ax.set_xlabel("Registered claim family")
    ax.set_ylabel("Manuscript section")
    fig.colorbar(image, ax=ax, label="primary figure count", fraction=0.045, pad=0.02)
    ax.text(
        0.02,
        -0.22,
        (
            f"{len(rows)} registered primary artifacts; counts classify declared claim tiers, not validation. "
            "The companion detail lists source classes and unsupported inferences."
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
    groups = _primary_figure_source_classes()
    artifact_count = sum(group["artifact_count"] for group in groups)
    fig, ax = plt.subplots(figsize=(11.8, max(6.4, 0.78 * len(groups) + 1.8)))
    ax.axis("off")
    columns = (
        (0.04, "Source class", 22),
        (0.255, "Artifacts (n)", 12),
        (0.395, "Declared family counts", 27),
        (0.72, "Claim ceiling", 29),
    )
    for x, title, _ in columns:
        ax.text(x, 0.91, title, transform=ax.transAxes, fontsize=10, weight="bold")
    step = 0.75 / max(1, len(groups))
    for index, group in enumerate(groups):
        y = 0.86 - (index + 0.5) * step
        ax.add_patch(
            Rectangle(
                (0.02, y - step * 0.46),
                0.96,
                step * 0.92,
                transform=ax.transAxes,
                facecolor="#F8FAFC" if index % 2 == 0 else "white",
                edgecolor="#E2E8F0",
                lw=0.6,
            )
        )
        values = (
            group["source_class"],
            str(group["artifact_count"]),
            "; ".join(f"{family}: {count}" for family, count in group["family_counts"].items()),
            group["claim_ceiling"],
        )
        for value, (x, _, width) in zip(values, columns, strict=True):
            ax.text(
                x,
                y,
                wrap_label(value, width=width),
                transform=ax.transAxes,
                va="center",
                fontsize=10,
                color="#111827",
            )
    ax.set_title("Primary-figure sources and claim ceilings", loc="left", pad=18)
    add_figure_note(
        fig,
        f"{artifact_count} registered primary artifacts across {len(groups)} source classes; counts are not evidence strength.\nPer-artifact source routes and full unsupported-inference statements remain in the registry / plot-data inventory and sidecars.",
        y=0.02,
    )
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


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
            "Rendered contact does not validate motion dynamics.",
            "pose/contact metadata",
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
        ("Rule class", 0.055),
        ("Claim-admission rule", 0.235),
        ("Evidence to inspect", 0.585),
        ("Claim ceiling", 0.795),
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
                wrap_label(value, width=36 if x == 0.235 else 24),
                transform=ax.transAxes,
                va="center",
                fontsize=9.2,
                color="#111827",
            )
    ax.text(
        0.5,
        0.09,
        "Conceptual rules, not a current evidence receipt: source payloads and artifact-specific metadata remain authoritative.",
        transform=ax.transAxes,
        ha="center",
        fontsize=9,
        color="#334155",
    )
    ax.set_title("Claim-admission rules (conceptual)", loc="left", pad=15)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def _scholarship_evidence_matrix(path: Path) -> Path:
    records = verified_source_refresh_ledger()
    fig, ax = plt.subplots(figsize=(14.0, max(6.2, 0.64 * len(records) + 2.0)))
    ax.axis("off")
    columns = (
        (0.035, "Source key", 29),
        (0.25, "DOI", 32),
        (0.49, "Declared tier", 21),
        (0.66, "Sections (n)", 12),
        (0.76, "Figures (n)", 12),
        (0.86, "Availability", 19),
    )
    for x, title, _ in columns:
        ax.text(x, 0.94, title, transform=ax.transAxes, fontsize=10, weight="bold")
    step = 0.83 / max(1, len(records))
    for index, record in enumerate(records):
        y = 0.91 - (index + 0.5) * step
        ax.add_patch(
            Rectangle(
                (0.02, y - 0.46 * step),
                0.96,
                0.92 * step,
                transform=ax.transAxes,
                facecolor="#F8FAFC" if index % 2 == 0 else "white",
                edgecolor="#E2E8F0",
                lw=0.5,
            )
        )
        ax.add_patch(
            Rectangle(
                (0.02, y - 0.46 * step),
                0.005,
                0.92 * step,
                transform=ax.transAxes,
                facecolor=_claim_color(record.claim_tier),
                lw=0,
            )
        )
        values = (
            record.citation_key,
            record.doi,
            record.claim_tier.replace("_", " "),
            str(len(record.section_targets)),
            str(len(record.figure_targets)),
            record.availability_status.replace("_", " "),
        )
        for value, (x, _, width) in zip(values, columns, strict=True):
            ax.text(
                x,
                y,
                textwrap.fill(value, width=width),
                transform=ax.transAxes,
                va="center",
                fontsize=9,
                color="#111827",
            )
    ax.set_title("Scholarly source ledger and availability", loc="left", pad=18)
    add_figure_note(
        fig,
        f"{len(records)} ledger sources; counts are manuscript mappings, not sample sizes.\nVerified DOI/source identity does not imply a local payload, parser success, or biological validation.",
        y=0.015,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path
