"""Markdown report builders for empirical BeeBrain ingest."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..utils import project_relative_path
from .empirical_data import EmpiricalWaggleFollowerDataset


def markdown_report(report: dict[str, Any], figure_paths: list[Path], project_root: Path) -> str:
    top = list(report["stack_alignment"].items())[:8]
    lines = [
        "# Empirical Bee Data Analysis",
        "",
        f"- Panels analyzed: `{report['panel_count']}`",
        f"- Workbook dataframe summaries: `{report['workbook_dataframe_summary_count']}`",
        f"- Calcium datasets parsed: `{report['calcium_dataset_count']}`",
        f"- Antennal movement summaries: `{report['antennal_movement_summary_count']}`",
        f"- Anatomy inventories parsed: `{report['anatomy_summary']['inventory_count']}`",
        f"- Neuropil abbreviations parsed: `{report['anatomy_summary']['neuropil_count']}`",
        f"- Templates integrated into BeeBrain: `{report['template_count']}`",
        f"- All quality checks passed: `{report['all_quality_checks_passed']}`",
        f"- Mean odor separability: `{report['activity_summary']['mean_odor_separability']:.3f}`",
        f"- Empirical drive label: `{report['empirical_drive_label']}`",
        f"- Empirical antennal vibration: `{report['empirical_antennal_vibration']}`",
        f"- Final stack empirical odor: `{report['simulation_summary_with_empirical_templates']['final_empirical_odor']}`",
        f"- Final stack empirical alignment: `{report['simulation_summary_with_empirical_templates']['final_empirical_alignment']:.3f}`",
        "",
        "## Top BeeBrain Alignments",
        "",
    ]
    for label, value in top:
        lines.append(f"- `{label}`: {value:.3f}")
    lines.extend(["", "## Anatomy Coverage", ""])
    lines.append(
        "- Downloaded assets: `{downloaded_asset_count}` of `{asset_count}`; "
        "VRML files `{vrml_file_count}`; TIFF files `{tiff_file_count}`; "
        "uncompressed bytes `{total_uncompressed_bytes}`.".format(**report["anatomy_summary"])
    )
    region_counts = report["anatomy_summary"]["major_regions"]
    if region_counts:
        for region, count in sorted(region_counts.items()):
            lines.append(f"- `{region}` abbreviations: `{count}`")
    else:
        lines.append("- No neuropil abbreviation table was available locally.")
    lines.extend(["", "## Activity Summary", ""])
    activity = report["activity_summary"]
    lines.append(
        f"- Calcium latency `{activity['calcium_mean_latency_s']:.3f}` s; "
        f"inhibitory fraction `{activity['calcium_inhibitory_fraction']:.3f}`; "
        f"excitatory fraction `{activity['calcium_excitatory_fraction']:.3f}`."
    )
    lines.append(
        f"- Aftersmell/post-odor response mean: `{activity['aftersmell_response_mean']:.3f}`"
    )
    for region, value in sorted(activity["region_response_means"].items()):
        lines.append(f"- `{region}` mean absolute response: `{value:.3f}`")
    lines.extend(["", "## Antennal Active Sensing", ""])
    for summary in report["antennal_movement_summaries"]:
        lines.append(
            "- `{dataset_id}`: rows `{row_count}`, bees `{bee_count}`, plumes `{plume_count}`, "
            "odor-on `{odor_on_fraction:.3f}`, left/right correlation `{left_right_theta_correlation:.3f}`".format(
                **summary
            )
        )
    if not report["antennal_movement_summaries"]:
        lines.append("- No frame-level antennal summaries were available in local archives.")
    waggle = report.get("waggle_follower_analysis") or {}
    if waggle:
        summary = waggle.get("summary", {})
        lines.extend(["", "## Waggle Follower Decoding", ""])
        lines.append(
            "- Hadjitofi-Webb follower tracks `{track_count}`; confidence `{confidence_score:.3f}`; "
            "angle/midpoint correlation `{follower_angle_midpoint_correlation:.3f}`; "
            "decoding improvement `{decoding_improvement_fraction:.3f}`.".format(**summary)
        )
    completeness = report.get("brain_data_completeness", {})
    if completeness:
        lines.extend(["", "## Brain Data Completeness", ""])
        lines.append(
            "- Curated datasets `{dataset_count}`; downloaded `{downloaded_dataset_count}`; "
            "parseable `{parseable_dataset_count}`; parseable fraction `{parseable_fraction:.3f}`; "
            "source-verified `{source_verified_dataset_count}`; target satisfied `{parseability_target_satisfied}`.".format(
                **completeness
            )
        )
    blocked_archives = [
        row for row in report["archive_status"] if not row.get("archive_downloaded")
    ]
    if blocked_archives:
        lines.extend(["", "## Archive Caveats", ""])
        for row in blocked_archives:
            lines.append(
                f"- `{row['dataset_id']}` was cataloged but not downloaded"
                f" ({row.get('archive_error') or 'file-level fallback did not produce a local file'})."
            )
    if report["known_gaps"]:
        lines.extend(["", "## Known Gaps", ""])
        for gap in report["known_gaps"]:
            lines.append(f"- {gap}.")
    lines.extend(["", "## Figures", ""])
    for path in figure_paths:
        lines.append(f"- `{project_relative_path(path, project_root)}`")
    lines.append("")
    return "\n".join(lines)


def waggle_markdown(
    waggle_dataset: EmpiricalWaggleFollowerDataset | None,
    data_completeness: Any,
    project_root: Path,
) -> str:
    lines = [
        "# Waggle Follower Analysis",
        "",
        "This report covers the curated Hadjitofi-Webb Figshare waggle-following source "
        "and its integration into BeeBrain/BeeSwarm waggle decoding.",
        "",
    ]
    if waggle_dataset is None:
        lines.extend(
            [
                "- Dataset status: `not local or not parseable`",
                "- Expected source: `https://figshare.com/articles/dataset/Honeybee_antennal_positioning_data_when_following_dances/24715977`",
                "- Regeneration command: `uv run python scripts/fetch_empirical_bee_data.py`",
                "",
            ]
        )
    else:
        summary = waggle_dataset.summary
        lines.extend(
            [
                "- Dataset status: `parsed`",
                f"- Tracks: `{summary.track_count}`",
                f"- Feature rows: `{summary.feature_row_count}`",
                f"- Binned rows: `{summary.binned_row_count}`",
                f"- Model-error rows: `{summary.model_error_row_count}`",
                f"- Follower angle/midpoint correlation: `{summary.follower_angle_midpoint_correlation:.3f}`",
                f"- Both-antennae decoding error: `{summary.both_antennae_mean_abs_error_deg:.3f}` deg",
                f"- No-antennae decoding error: `{summary.no_antennae_mean_abs_error_deg:.3f}` deg",
                f"- Decoding improvement fraction: `{summary.decoding_improvement_fraction:.3f}`",
                f"- Confidence score: `{summary.confidence_score:.3f}`",
                "",
                "## Source Files",
                "",
            ]
        )
        lines.extend(
            f"- `{project_relative_path(Path(path), project_root)}`"
            for path in waggle_dataset.source_files[:24]
        )
        lines.append("")
    completeness = data_completeness.as_dict()
    lines.extend(
        [
            "## BeeBrain Data Completeness",
            "",
            f"- Curated datasets: `{completeness['dataset_count']}`",
            f"- Downloaded datasets: `{completeness['downloaded_dataset_count']}`",
            f"- Parseable datasets: `{completeness['parseable_dataset_count']}`",
            f"- Parseable fraction: `{completeness['parseable_fraction']:.3f}`",
            f"- Source-verified datasets: `{completeness['source_verified_dataset_count']}`",
            f"- Source-verified blockers: `{completeness['source_verified_blocked_count']}`",
            f"- Parseability target satisfied: `{completeness['parseability_target_satisfied']}`",
            "",
        ]
    )
    return "\n".join(lines)


def select_drive_label(templates: dict[str, Any]) -> str:
    preferred = ("alarm", "isopentyl acetate", "16ol", "1-octanol")
    for label in preferred:
        if label in templates:
            return label
    return sorted(templates)[0]


def _dataset_id_from_path(source_dir: Path, path: Path) -> str:
    relative = path.relative_to(source_dir)
    return relative.parts[0]
