from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from beestack.brain import (
    BeeBrainActivitySummary,
    BeeBrainAnatomySummary,
    BeeBrainEndToEndReport,
)
from beestack.brain.empirical_data import (
    EmpiricalWaggleFollowerDataset,
    WaggleFollowerSummary,
    WaggleFollowerTrack,
)


def _analysis_script() -> ModuleType:
    project_root = Path(__file__).resolve().parents[1]
    scripts_dir = project_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    spec = importlib.util.spec_from_file_location(
        "analyze_empirical_bee_data_for_tests",
        scripts_dir / "analyze_empirical_bee_data.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _activity_summary() -> BeeBrainActivitySummary:
    return BeeBrainActivitySummary(
        panel_count=1,
        calcium_dataset_count=0,
        antennal_movement_summary_count=0,
        template_count=1,
        all_quality_checks_passed=True,
        mean_odor_separability=0.5,
        calcium_mean_latency_s=0.0,
        calcium_inhibitory_fraction=0.0,
        calcium_excitatory_fraction=0.0,
        aftersmell_response_mean=0.0,
        region_response_means={},
        antennal_active_sensing_drive={},
        neuromodulatory_defence_summary={},
    )


def _anatomy_summary() -> BeeBrainAnatomySummary:
    return BeeBrainAnatomySummary(
        dataset_id="virtual-honeybee-standard-brain",
        asset_count=1,
        downloaded_asset_count=1,
        inventory_count=1,
        neuropil_count=1,
        bilateral_pair_count=0,
        vrml_file_count=1,
        tiff_file_count=0,
        total_uncompressed_bytes=128,
        major_regions={},
    )


def _minimal_empirical_report() -> dict[str, Any]:
    return {
        "panel_count": 1,
        "workbook_dataframe_summary_count": 1,
        "calcium_dataset_count": 0,
        "antennal_movement_summary_count": 0,
        "anatomy_summary": {
            "inventory_count": 1,
            "neuropil_count": 1,
            "downloaded_asset_count": 1,
            "asset_count": 1,
            "vrml_file_count": 1,
            "tiff_file_count": 0,
            "total_uncompressed_bytes": 128,
            "major_regions": {},
        },
        "template_count": 1,
        "all_quality_checks_passed": True,
        "activity_summary": {
            "mean_odor_separability": 0.5,
            "calcium_mean_latency_s": 0.0,
            "calcium_inhibitory_fraction": 0.0,
            "calcium_excitatory_fraction": 0.0,
            "aftersmell_response_mean": 0.0,
            "region_response_means": {},
        },
        "empirical_drive_label": "alarm",
        "empirical_antennal_vibration": None,
        "simulation_summary_with_empirical_templates": {
            "final_empirical_odor": "alarm",
            "final_empirical_alignment": 0.5,
        },
        "stack_alignment": {"alarm": 0.5},
        "antennal_movement_summaries": [],
        "waggle_follower_analysis": {},
        "brain_data_completeness": {
            "dataset_count": 5,
            "downloaded_dataset_count": 3,
            "parseable_dataset_count": 3,
            "parseable_fraction": 0.6,
            "source_verified_dataset_count": 3,
            "parseability_target_satisfied": False,
        },
        "archive_status": [],
        "known_gaps": [],
    }


def test_bee_brain_end_to_end_report_normalizes_project_local_paths() -> None:
    project_root = Path(__file__).resolve().parents[1]
    report = BeeBrainEndToEndReport(
        anatomy=_anatomy_summary(),
        activity=_activity_summary(),
        dataset_ids=("fixture",),
        figure_paths=(
            str(project_root / "output" / "figures" / "empirical" / "panel.png"),
        ),
        archive_status=(),
        anatomy_downloads=(
            {
                "dataset_id": "virtual-honeybee-standard-brain",
                "local_path": str(
                    project_root
                    / "output"
                    / "data"
                    / "empirical_sources"
                    / "virtual-honeybee-standard-brain"
                    / "VRML.zip"
                ),
            },
        ),
        known_gaps=(),
    )

    payload = report.as_dict()

    assert payload["figure_paths"] == ("output/figures/empirical/panel.png",)
    assert payload["anatomy_downloads"][0]["local_path"] == (
        "output/data/empirical_sources/virtual-honeybee-standard-brain/VRML.zip"
    )


def test_empirical_markdown_reports_repo_relative_figure_paths() -> None:
    project_root = Path(__file__).resolve().parents[1]
    module = _analysis_script()
    markdown = module._markdown_report(
        _minimal_empirical_report(),
        [project_root / "output" / "figures" / "empirical" / "panel.png"],
    )

    assert str(project_root) not in markdown
    assert "`output/figures/empirical/panel.png`" in markdown


def test_waggle_markdown_reports_repo_relative_source_files() -> None:
    project_root = Path(__file__).resolve().parents[1]
    module = _analysis_script()
    source_file = (
        project_root
        / "output"
        / "data"
        / "empirical_sources"
        / "figshare-hadjitofi-2024-waggle-following"
        / "files"
        / "features.csv"
    )
    dataset = EmpiricalWaggleFollowerDataset(
        dataset_id="figshare-hadjitofi-2024-waggle-following",
        tracks=(
            WaggleFollowerTrack(
                bee_id="n1",
                row_count=1,
                frame_min=0,
                frame_max=1,
                mean_angle_to_dancer_deg=0.0,
                mean_dancer_angle_to_gravity_deg=0.0,
                mean_left_antenna_deg=0.0,
                mean_right_antenna_deg=0.0,
                mean_antenna_midpoint_deg=0.0,
                mean_scape_angle_deg=0.0,
                left_right_antenna_synchrony=0.0,
            ),
        ),
        summary=WaggleFollowerSummary(
            dataset_id="figshare-hadjitofi-2024-waggle-following",
            track_count=1,
            feature_row_count=1,
            binned_row_count=0,
            model_error_row_count=0,
            straightness_row_count=0,
            frame_min=0,
            frame_max=1,
            mean_angle_to_dancer_deg=0.0,
            mean_dancer_angle_to_gravity_deg=0.0,
            mean_left_antenna_deg=0.0,
            mean_right_antenna_deg=0.0,
            mean_antenna_midpoint_deg=0.0,
            mean_scape_angle_deg=0.0,
            follower_angle_midpoint_correlation=0.0,
            left_right_antenna_synchrony=0.0,
            mean_abs_vector_error_deg=0.0,
            no_antennae_mean_abs_error_deg=0.0,
            both_antennae_mean_abs_error_deg=0.0,
            decoding_improvement_fraction=0.0,
            straightness_mean=0.0,
            confidence_score=0.0,
        ),
        source_files=(str(source_file),),
    )

    class Completeness:
        def as_dict(self) -> dict[str, object]:
            return {
                "dataset_count": 5,
                "downloaded_dataset_count": 3,
                "parseable_dataset_count": 3,
                "parseable_fraction": 0.6,
                "source_verified_dataset_count": 3,
                "source_verified_blocked_count": 2,
                "parseability_target_satisfied": False,
            }

    markdown = module._waggle_markdown(dataset, Completeness())

    assert str(project_root) not in markdown
    assert (
        "`output/data/empirical_sources/figshare-hadjitofi-2024-waggle-following/files/features.csv`"
        in markdown
    )
