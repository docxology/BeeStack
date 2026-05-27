#!/usr/bin/env python3
"""Thin orchestrator for empirical BeeBrain dataset analysis."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack import BeeStackConfig, config_from_mapping  # noqa: E402
from beestack.brain.empirical_ingest_reports import markdown_report, waggle_markdown  # noqa: E402
from beestack.brain.empirical_pipeline import build_empirical_analysis_bundle  # noqa: E402
from beestack.documentation_signpost import finalize_project_outputs  # noqa: E402
from beestack.orchestrator import run_simulation  # noqa: E402
from beestack.utils import project_relative_path, project_relative_payload, write_json  # noqa: E402
from beestack.visualization import generate_empirical_figures  # noqa: E402
from beestack.visualization.connectome_figures import generate_connectome_figures  # noqa: E402


def load_config() -> BeeStackConfig:
    config_path = PROJECT_ROOT / "manuscript" / "config.yaml"
    if not config_path.exists():
        return BeeStackConfig()
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return config_from_mapping(payload.get("beestack", payload))


def run_empirical_analysis(cfg: BeeStackConfig, project_root: Path) -> bool:
    """Analyze empirical sources when panels exist; return False when skipped offline."""

    bundle = build_empirical_analysis_bundle(cfg, project_root)
    if bundle is None:
        return False
    result = run_simulation(
        cfg,
        steps=24,
        empirical_odor_templates=bundle.bank.templates,
        empirical_drive=bundle.empirical_drive,
        empirical_antennal_vibration=bundle.empirical_vibration,
    )
    data_dir = project_root / "output" / "data"
    figure_paths = generate_empirical_figures(
        bundle.panels,
        bundle.stats,
        bundle.alignment,
        project_root / "output" / "figures" / "empirical",
        antennal_summaries=bundle.antennal_summaries,
        anatomy_summary=bundle.anatomy_summary,
        anatomy_inventories=bundle.anatomy_inventories,
        neuropil_abbreviations=bundle.neuropil_abbreviations,
        activity_summary=bundle.activity_summary,
        waggle_summary=bundle.waggle_dataset.summary if bundle.waggle_dataset is not None else None,
        data_completeness=bundle.data_completeness,
        connectome_report=bundle.connectome_report,
    )
    end_to_end_report = bundle.end_to_end_report.__class__(
        anatomy=bundle.anatomy_summary,
        activity=bundle.activity_summary,
        dataset_ids=bundle.end_to_end_report.dataset_ids,
        figure_paths=tuple(project_relative_path(path, project_root) for path in figure_paths),
        archive_status=bundle.end_to_end_report.archive_status,
        anatomy_downloads=tuple(
            project_relative_payload(record.as_dict(), project_root)
            for record in bundle.anatomy_records
        ),
        known_gaps=bundle.known_gap_list,
    )
    report = dict(bundle.report)
    report["simulation_summary_with_empirical_templates"] = result.summary()
    report["end_to_end_report"] = end_to_end_report.as_dict()
    write_json(data_dir / "empirical_analysis.json", report, project_root=project_root)
    write_json(
        data_dir / "empirical_template_bank.json",
        bundle.bank.as_dict(),
        project_root=project_root,
    )
    write_json(
        data_dir / "bee_brain_end_to_end_report.json",
        end_to_end_report.as_dict(),
        project_root=project_root,
    )
    write_json(
        data_dir / "waggle_follower_analysis.json",
        bundle.waggle_dataset.as_dict()
        if bundle.waggle_dataset is not None
        else {"dataset_id": "missing"},
        project_root=project_root,
    )
    write_json(
        data_dir / "brain_data_completeness.json",
        bundle.data_completeness.as_dict(),
        project_root=project_root,
    )
    write_json(
        data_dir / "bee_brain_connectome.json",
        bundle.connectome_report.as_dict(),
        project_root=project_root,
    )
    connectome_paths = generate_connectome_figures(
        bundle.connectome_report,
        project_root / "output" / "figures" / "empirical",
        completeness_tiers=bundle.data_completeness.connectome_tiers,
    )
    figure_paths = list(figure_paths) + connectome_paths
    reports_dir = project_root / "output" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.joinpath("empirical_analysis.md").write_text(
        markdown_report(report, list(figure_paths), project_root),
        encoding="utf-8",
    )
    reports_dir.joinpath("waggle_follower_analysis.md").write_text(
        waggle_markdown(bundle.waggle_dataset, bundle.data_completeness, project_root),
        encoding="utf-8",
    )
    finalize_project_outputs(project_root)
    return True


def main() -> None:
    cfg = load_config()
    if not run_empirical_analysis(cfg, PROJECT_ROOT):
        print(
            "[SKIP] analyze_empirical_bee_data: no empirical panels found "
            "(network-gated — run scripts/fetch_empirical_bee_data.py to enable). "
            "Skipping empirical analysis; expected in the offline core pipeline.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
