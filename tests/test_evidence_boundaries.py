from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from beestack.brain import DanceVector
from beestack.brain.empirical import summarize_calcium_trials
from beestack.brain.empirical_data import (
    EmpiricalOdorResponsePanel,
    calcium_dataset_from_trial_array,
    response_templates_from_calcium_dataset,
    summarize_antennal_movement_rows,
    summarize_waggle_follower_rows,
    waggle_vibration_from_followers,
)
from beestack.brain.empirical_pipeline import integrated_template_bank
from beestack.config import config_from_mapping
from beestack.mind import initial_belief
from beestack.research.methods_assembly import (
    assemble_methods_analysis_report,
    manuscript_figure_index,
)
from beestack.research.suite import assemble_research_suite_report, run_sensitivity_sweeps
from beestack.swarm.communication import dance_recruitment_diagnostics
from beestack.swarm.state import BeeAgent
from beestack.utils import project_relative_path, project_relative_payload
from beestack.visualization.bee_signature import analyze_bee_render_signature
from beestack.visualization.figure_metadata import write_figure_artifacts
from beestack.visualization.figure_plot_specs import empirical_plot_data


def _followers(errors):
    return summarize_waggle_follower_rows(
        ({"bee_id": "b", "frame": 0, "angle_to_dancer_deg": 0},),
        model_error_rows=tuple(
            {"_source_file": f"{condition}-errors.csv", "vector_error_deg": value}
            for condition, value in errors
        ),
    ).summary


def _plot(path, **kwargs):
    return empirical_plot_data(Path(path), panels=(), panel_stats=(), stack_alignment={}, **kwargs)


@pytest.mark.parametrize(
    "errors,no_error,both_error,improvement,counts",
    [
        ((("no_antennae", 20.0),), 20.0, None, None, (1, 0)),
        ((("both_antennae", 0.0),), None, 0.0, None, (0, 1)),
        ((), None, None, None, (0, 0)),
        ((("no_antennae", 20.0), ("both_antennae", 0.0)), 20.0, 0.0, 1.0, (1, 1)),
        ((("no_antennae", 0.0), ("both_antennae", 0.0)), 0.0, 0.0, None, (1, 1)),
    ],
)
def test_error_absence_is_not_observed_zero(errors, no_error, both_error, improvement, counts):
    summary = _followers(errors)
    assert summary.no_antennae_mean_abs_error_deg == no_error
    assert summary.both_antennae_mean_abs_error_deg == both_error
    assert summary.decoding_improvement_fraction == improvement
    assert (summary.no_antennae_error_count, summary.both_antennae_error_count) == counts
    assert summary.confidence_score == pytest.approx(0.3 if improvement == 1.0 else 0.0)
    assert waggle_vibration_from_followers(summary)[0] == pytest.approx(
        0.35 if improvement == 1.0 else 0.0
    )
    payload = _plot("beeswarm_waggle_recruitment_diagnostics.png", waggle_summary=summary)
    assert payload["values"] == [no_error, summary.mean_abs_vector_error_deg, both_error]
    assert payload["both_antennae_error_count"] == counts[1]
    json.dumps(payload, allow_nan=False)


def test_missing_both_antennae_cannot_supply_perfect_alignment():
    cfg = config_from_mapping({})
    features = tuple(
        {"bee_id": "b", "frame": index, "angle_to_dancer_deg": angle, "antenna_midpoint_deg": angle}
        for index, angle in enumerate((10, 20, 30))
    )
    no_antennae = {"_source_file": "no_antennae-errors.csv", "vector_error_deg": 20.0}
    both_antennae = {"_source_file": "both_antennae-errors.csv", "vector_error_deg": 0.0}
    missing = summarize_waggle_follower_rows(features, model_error_rows=(no_antennae,)).summary
    observed = summarize_waggle_follower_rows(
        features, model_error_rows=(no_antennae, both_antennae)
    ).summary
    belief = replace(
        initial_belief(cfg), caste_probs={"forager": 1.0}, colony_need={"food_need": 0.9}
    )
    followers = (BeeAgent(1, 20.0, "forager", np.zeros(3), 1.0, belief),)
    dance = DanceVector(1.0, 0.0, 1.0, 1.0)
    unavailable = dance_recruitment_diagnostics(dance, followers, cfg, waggle_summary=missing)
    measured = dance_recruitment_diagnostics(dance, followers, cfg, waggle_summary=observed)
    assert unavailable.follower_alignment_score is None
    assert unavailable.as_dict()["follower_alignment_score"] is None
    assert measured.follower_alignment_score == 1.0
    assert missing.confidence_score > 0
    assert unavailable.mean_follow_probability == 0.0
    assert measured.mean_follow_probability > 0.0


def test_movement_channels_use_their_own_observations():
    summary = summarize_antennal_movement_rows(({"LeftTheta": 10}, {"RightTheta": 20}))
    assert summary.mean_abs_left_theta_deg == 10
    assert summary.mean_abs_right_theta_deg == 20
    assert (summary.left_theta_observation_count, summary.right_theta_observation_count) == (1, 1)
    absent = summarize_antennal_movement_rows(({"LeftTheta": 0},))
    assert absent.mean_abs_left_theta_deg == 0
    assert absent.mean_abs_right_theta_deg is None
    assert absent.right_theta_observation_count == 0
    payload = _plot("empirical_antennal_movement.png", antennal_summaries=(absent,))
    assert payload["values"][1:3] == [0.0, None]
    json.dumps(payload, allow_nan=False)


def test_calcium_templates_require_recorded_protocol_windows():
    cfg = config_from_mapping({})
    dataset = calcium_dataset_from_trial_array(
        "fixture", np.arange(1.0, 6.0).reshape(1, 1, 1, 5, 1), 100.0, ("odor",), ("g",)
    )
    with pytest.raises(ValueError, match="baseline|stimulus"):
        response_templates_from_calcium_dataset(dataset, cfg)
    with pytest.raises(ValueError, match="baseline|stimulus"):
        integrated_template_bank(
            (
                EmpiricalOdorResponsePanel(
                    "fixture",
                    np.array([[1.0, 2.0], [2.0, 1.0]]),
                    ("a", "b"),
                    ("left", "right"),
                    "fixture",
                    "response",
                ),
            ),
            (dataset,),
            cfg,
        )
    protocol = replace(dataset.protocol(cfg), baseline_s=0.01, stimulus_s=(0.01, 0.04))
    expected = summarize_calcium_trials(dataset.traces, protocol).mean_response[0]
    template = response_templates_from_calcium_dataset(dataset, cfg, protocol)["odor"]
    np.testing.assert_allclose(template, expected / abs(expected))
    for baseline_s, stimulus_s in (
        (0, (0.01, 0.04)),
        (0.06, (0.01, 0.04)),
        (0.01, (0.05, 0.06)),
        (0.01, (0.03, 0.02)),
    ):
        with pytest.raises(ValueError, match="baseline|stimulus"):
            response_templates_from_calcium_dataset(
                dataset, cfg, replace(protocol, baseline_s=baseline_s, stimulus_s=stimulus_s)
            )


def _sidecars(root):
    return {
        str(root / "output/figures/renders/beebody_contact_sheet.png"): {
            "backend": "FlyBody/MuJoCo",
            "fidelity": "real_flybody_3d contact sheet",
            "source_data": "output/animations/body.xml",
            "validation_status": "contact_verified",
            "regeneration_command": "uv run python scripts/generate_animations.py",
            "availability_status": "generated",
        },
        "output/figures/empirical/empirical_panel_heatmap.png": {
            "backend": "Matplotlib empirical-data renderer",
            "fidelity": "empirical panel summary",
            "source_data": "output/data/empirical_analysis.json",
            "validation_status": "parsed",
            "regeneration_command": "uv run python scripts/analyze_empirical_bee_data.py",
            "availability_status": "historical_unavailable",
        },
        "output/figures/research/research_scorecard_heatmap.png": {
            "backend": "Matplotlib",
            "fidelity": "research_diagnostic",
            "source_data": "output/reports/research_suite_report.json",
            "validation_status": "nonblank",
            "regeneration_command": "uv run python scripts/run_research_suite.py",
            "availability_status": "generated",
        },
    }


def test_unique_inventory_preserves_sidecar_provenance_through_index(tmp_path):
    cfg = config_from_mapping({})
    sweeps = run_sensitivity_sweeps(cfg)
    metadata = _sidecars(tmp_path)
    paths = (
        *metadata,
        "output/figures/renders/beebody_contact_sheet.png",
        *metadata,
        "./output/figures/research/../research/research_scorecard_heatmap.png",
    )
    reports = [
        assemble_research_suite_report(
            cfg,
            simulation_summary={},
            animation_manifest={},
            integrity_review={},
            empirical_analysis={},
            figure_paths=paths,
            interactive_paths=(),
            sensitivity_sweeps=sweeps,
            project_root=tmp_path,
            artifact_metadata=metadata,
        )
        for _ in range(2)
    ]
    assert reports[0].as_dict() == reports[1].as_dict()
    artifacts = reports[0].as_dict()["visualization_artifacts"]
    assert len(artifacts) == 3
    assert [row["path"] for row in artifacts] == sorted({row["path"] for row in artifacts})
    previous = reports[0].as_dict()
    previous["visualization_artifacts"] = [
        {
            **row,
            "backend": "generic",
            "fidelity_level": "research_diagnostic",
            "source_data": "generic",
            "regeneration_command": "generic",
        }
        for row in artifacts
    ]
    methods = assemble_methods_analysis_report(
        cfg,
        simulation_records=(),
        simulation_summary={},
        animation_manifest={},
        research_report=previous,
        empirical_analysis={},
        integrity_review={},
        figure_paths=paths,
        project_root=tmp_path,
        artifact_metadata=metadata,
    )
    index = {
        row["artifact_path"]: row for row in manuscript_figure_index(methods, project_root=tmp_path)
    }
    panels = {
        path: (panel, i)
        for panel in methods.module_panels
        for i, path in enumerate(panel.visualization_panel.artifact_paths)
    }
    for path, original in metadata.items():
        key = project_relative_path(path, tmp_path)
        record = next(row for row in artifacts if row["path"] == key)
        for field in (
            "backend",
            "source_data",
            "validation_status",
            "regeneration_command",
            "availability_status",
        ):
            assert record[field] == original[field]
            assert index[key][field] == original[field]
        assert record["fidelity_level"] == index[key]["fidelity_level"] == original["fidelity"]
        if key in panels:
            panel, i = panels[key]
            assert panel.visualization_panel.source_data[i] == original["source_data"]
            assert (
                panel.visualization_panel.regeneration_commands[i]
                == original["regeneration_command"]
            )
            assert (
                panel.visualization_panel.availability_statuses[i]
                == original["availability_status"]
            )


def test_root_aware_json_sidecars_are_cwd_invariant(tmp_path, monkeypatch):
    root = tmp_path / "project"
    directory = root / "output/figures"
    directory.mkdir(parents=True)
    figure = directory / "custom.png"
    Image.fromarray(np.arange(32 * 32 * 3, dtype=np.uint8).reshape(32, 32, 3)).save(figure)
    outside = tmp_path / "sibling/source.json"
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    snapshots = []
    for cwd in (root, tmp_path, unrelated):
        monkeypatch.chdir(cwd)
        write_figure_artifacts(
            figure,
            {"source": str(root / "output/data/source.json"), "outside": str(outside)},
            title="Fixture",
            backend="fixture",
            fidelity="diagnostic",
            source_data=str(root / "output/data/source.json"),
            validation_status="generated",
            regeneration_command="fixture",
            project_root=root,
        )
        snapshots.append(
            (
                figure.with_suffix(".json").read_bytes(),
                figure.with_name("custom_data.json").read_bytes(),
            )
        )
        assert project_relative_path(figure) == str(figure)
        assert (
            project_relative_payload({"path": str(figure)}, root)["path"]
            == "output/figures/custom.png"
        )
    assert snapshots[0] == snapshots[1] == snapshots[2]
    metadata, data = (json.loads(body) for body in snapshots[0])
    assert metadata["figure_path"] == "output/figures/custom.png"
    assert metadata["source_data"] == data["source"] == "output/data/source.json"
    assert metadata["plot_data_path"] == "output/figures/custom_data.json"
    assert data["outside"] == str(outside)


def test_periodic_motion_is_not_erased_by_matching_endpoints():
    first = np.full((12, 12, 3), 120, dtype=np.uint8)
    middle = first.copy()
    middle[:6, :6] = 180
    periodic = analyze_bee_render_signature([first, middle, first], '<mujoco model="apis"/>')
    static = analyze_bee_render_signature([first, first, first], '<mujoco model="apis"/>')
    assert periodic.motion_pixels == 108
    assert periodic.mean_adjacent_motion_pixels == 108
    assert periodic.locomotion_score == 1.0
    assert static.motion_pixels == static.locomotion_score == 0
    assert not static.bee_like


def test_dataset_json_preserves_paths_until_root_aware_serialization(tmp_path, monkeypatch):
    root = tmp_path / "project"
    root.mkdir()
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    dataset = summarize_waggle_follower_rows(
        ({"bee_id": "b", "frame": 0, "angle_to_dancer_deg": 0},),
    )
    source = root / "output/data/features.csv"
    dataset = replace(dataset, source_files=(str(source),))
    snapshots = []
    for cwd in (root, tmp_path, unrelated):
        monkeypatch.chdir(cwd)
        unnormalized = dataset.as_dict()
        assert unnormalized["source_files"] == (str(source),)
        snapshots.append(json.dumps(dataset.as_dict(root), sort_keys=True))
        assert project_relative_payload(unnormalized, root) == dataset.as_dict(root)
    assert snapshots[0] == snapshots[1] == snapshots[2]
    assert json.loads(snapshots[0])["source_files"] == ["output/data/features.csv"]
