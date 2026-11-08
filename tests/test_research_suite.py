from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from beestack import (
    EmpiricalEvidenceRecord,
    ModuleMethodScorecard,
    ResearchSuiteReport,
    ResearchValidationRecord,
    SensitivitySweepResult,
    VisualizationArtifactRecord,
    assemble_research_suite_report,
    config_from_mapping,
    run_sensitivity_sweeps,
    run_simulation,
    stack_integrity_review,
)
from beestack.visualization import generate_research_figures


def _manifest() -> dict[str, object]:
    return {
        "animations": [
            {
                "path": "/tmp/beebody.gif",
                "backend": "flybody.walk_imitation+rollout_and_render",
                "render_backend": "flybody.walk_imitation+rollout_and_render",
                "source": "/tmp/apis_mellifera_worker.xml",
                "contact_sheet": "/tmp/beebody_contact_sheet.png",
                "fidelity_level": "real_flybody_3d",
            },
            {
                "path": "/tmp/beeswarm_10_beebody_collision.gif",
                "backend": "flybody-generated-mjcf+mujoco.MjModel+MjData+Renderer",
                "render_backend": "flybody-generated-mjcf+mujoco.MjModel+MjData+Renderer",
                "scene_xml": "/tmp/collision.xml",
                "contact_sheet": "/tmp/collision_contact_sheet.png",
                "fidelity_level": "real_flybody_3d_contact_physics",
            },
        ],
        "groups": {
            "real_flybody_3d": [
                "/tmp/beebody_flybody_morphology.gif",
                "/tmp/beebody_flybody_flight.gif",
                "/tmp/beeswarm_10_beebody_collision.gif",
                "/tmp/beeswarm_waggle_dance_configured.gif",
                "/tmp/beeswarm_waggle_dance_long.gif",
            ]
        },
        "bee_visual_signature": {
            "bee_like": True,
            "score": 0.98,
            "silhouette_score": 1.0,
        },
        "flybody_contact_physics": {
            "passed": True,
            "scene_count": 2,
            "scenes": [
                {
                    "scene_name": "collision",
                    "metrics": {
                        "bee_bee_contact_count": 12,
                        "floor_contact_count": 1,
                        "unique_bee_contact_pair_count": 6,
                        "contact_graph_edge_count": 6,
                    },
                },
                {
                    "scene_name": "waggle",
                    "metrics": {
                        "bee_bee_contact_count": 8,
                        "floor_contact_count": 4,
                        "unique_bee_contact_pair_count": 3,
                        "follower_orientation_error_mean_deg": 18.0,
                        "follower_orientation_confidence": 0.78,
                        "follower_distance_mean_m": 0.11,
                        "follower_distance_std_m": 0.012,
                        "waggle_phase_coupling_score": 0.62,
                        "contact_graph_edge_count": 3,
                    },
                },
            ],
        },
    }


def _empirical() -> dict[str, object]:
    return {
        "panel_count": 4,
        "calcium_dataset_count": 1,
        "template_bank": {"template_count": 6},
        "activity_summary": {
            "mean_odor_separability": 0.42,
        },
        "anatomy_summary": {
            "inventory_count": 3,
            "downloaded_asset_count": 3,
        },
        "brain_data_completeness": {
            "parseable_fraction": 0.8,
            "source_verified_fraction": 1.0,
            "parseability_target_satisfied": True,
        },
    }


def test_research_records_reject_nonfinite_payloads() -> None:
    validation = ResearchValidationRecord("finite", True, 1.0, ">= 0", "finite check")
    scorecard = ModuleMethodScorecard(
        "BeeBody",
        "FlyBody",
        {"score": 1.0},
        (validation,),
        ("evidence",),
        ("gap",),
    )
    assert scorecard.as_dict()["validation_fraction"] == 1.0
    with pytest.raises(ValueError, match="finite"):
        ModuleMethodScorecard(
            "BeeBody",
            "FlyBody",
            {"bad": float("nan")},
            (validation,),
            ("evidence",),
            ("gap",),
        )
    with pytest.raises(ValueError, match="nonempty"):
        VisualizationArtifactRecord("", "figure", "matplotlib", "diagnostic", "data", "cmd", "ok")
    with pytest.raises(ValueError, match="finite"):
        SensitivitySweepResult("bad", (0.0, np.nan), {"x": (1.0, 2.0)}, "bad")


def test_research_record_validation_branches_are_explicit() -> None:
    validation = ResearchValidationRecord("finite", True, 1.0, ">= 0", "finite check")
    scorecard = ModuleMethodScorecard(
        "BeeBody",
        "FlyBody",
        {"score": 1.0},
        (validation,),
        ("evidence",),
        ("gap",),
    )
    visual = VisualizationArtifactRecord(
        "/tmp/figure.png",
        "figure",
        "matplotlib",
        "diagnostic",
        "fixture",
        "uv run python scripts/run_research_suite.py",
        "nonblank",
    )
    evidence = EmpiricalEvidenceRecord("dataset", "calcium", 1, 0.5, "template", "parsed", "")
    sweep = SensitivitySweepResult("x", (0.0, 1.0), {"y": (0.1, 0.2)}, "ok")

    for args in (
        ("", True, 1.0, ">= 0", "detail"),
        ("finite", True, 1.0, ">= 0", ""),
    ):
        with pytest.raises(ValueError):
            ResearchValidationRecord(*args)

    for args in (
        ("", "real", {"score": 1.0}, (validation,), ("evidence",), ("gap",)),
        ("BeeBody", "", {"score": 1.0}, (validation,), ("evidence",), ("gap",)),
        ("BeeBody", "real", {}, (validation,), ("evidence",), ("gap",)),
        ("BeeBody", "real", {"": 1.0}, (validation,), ("evidence",), ("gap",)),
        ("BeeBody", "real", {"bad": float("nan")}, (validation,), ("evidence",), ("gap",)),
        ("BeeBody", "real", {"score": 1.0}, (), ("evidence",), ("gap",)),
        ("BeeBody", "real", {"score": 1.0}, (validation,), (), ("gap",)),
        ("BeeBody", "real", {"score": 1.0}, (validation,), ("evidence",), ()),
    ):
        with pytest.raises(ValueError):
            ModuleMethodScorecard(*args)

    for args in (
        ("", "calcium", 1, 0.5, "template", "parsed", ""),
        ("dataset", "", 1, 0.5, "template", "parsed", ""),
        ("dataset", "calcium", -1, 0.5, "template", "parsed", ""),
        ("dataset", "calcium", 1, 1.5, "template", "parsed", ""),
        ("dataset", "calcium", 1, 0.5, "", "parsed", ""),
        ("dataset", "calcium", 1, 0.5, "template", "bad_status", ""),
    ):
        with pytest.raises(ValueError):
            EmpiricalEvidenceRecord(*args)

    for args in (
        ("", (0.0, 1.0), {"y": (0.1, 0.2)}, "ok"),
        ("x", (0.0,), {"y": (0.1,)}, "ok"),
        ("x", (0.0, 1.0), {}, "ok"),
        ("x", (0.0, 1.0), {"y": (0.1,)}, "ok"),
        ("x", (0.0, 1.0), {"y": (0.1, 0.2)}, ""),
    ):
        with pytest.raises(ValueError):
            SensitivitySweepResult(*args)

    for kwargs in (
        {"title": ""},
        {"summary": ""},
        {"module_scorecards": ()},
        {"visualization_artifacts": ()},
        {"overall_validation_fraction": 1.5},
        {"known_gaps": ()},
    ):
        with pytest.raises(ValueError):
            ResearchSuiteReport(
                kwargs.get("title", "Research"),
                kwargs.get("summary", "Summary"),
                kwargs.get("module_scorecards", (scorecard,)),
                kwargs.get("visualization_artifacts", (visual,)),
                (evidence,),
                (sweep,),
                kwargs.get("overall_validation_fraction", 1.0),
                kwargs.get("known_gaps", ("gap",)),
            )


def test_research_report_renders_current_source_states(tmp_path: Path) -> None:
    cfg = config_from_mapping({"research": {"scenario_count": 2, "sensitivity_sweep_size": 3}})
    summary = run_simulation(cfg, steps=2).summary()
    sweeps = run_sensitivity_sweeps(cfg)
    report = assemble_research_suite_report(
        cfg,
        simulation_summary=summary,
        animation_manifest=_manifest(),
        integrity_review=stack_integrity_review(cfg).as_dict(),
        empirical_analysis=_empirical(),
        figure_paths=("/tmp/body_energy_timeseries.png",),
        interactive_paths=(),
        sensitivity_sweeps=sweeps,
    )
    payload = json.loads(json.dumps(report.as_dict(), allow_nan=False))
    assert len(payload["module_scorecards"]) == 5
    assert payload["empirical_availability_counts"]["parsed"] >= 1
    generate_research_figures(report, tmp_path / "figures")
    raw = json.loads(
        (tmp_path / "figures" / "research_empirical_completeness_data.json").read_text()
    )
    rows = {row["dataset_id"]: row for row in raw["rows"]}
    assert rows["empirical-panels"]["availability_status"] == "parsed"
    assert rows["template-bank"]["availability_status"] == "generated"


def test_no_current_analysis_is_not_standalone_payload_absence(tmp_path: Path) -> None:
    cfg = config_from_mapping({"research": {"scenario_count": 2, "sensitivity_sweep_size": 3}})
    report = assemble_research_suite_report(
        cfg,
        simulation_summary={},
        animation_manifest=_manifest(),
        integrity_review={},
        empirical_analysis={},
        figure_paths=("output/figures/beestack_graphical_abstract.png",),
        interactive_paths=(),
        sensitivity_sweeps=run_sensitivity_sweeps(cfg),
        project_root=tmp_path,
    )
    assert {row.availability_status for row in report.empirical_evidence} == {
        "analysis_unavailable"
    }
    assert {row.local_records for row in report.empirical_evidence} == {0}
    assert report.empirical_availability_counts["parsed"] == 0
    assert report.empirical_availability_counts["generated"] == 0
