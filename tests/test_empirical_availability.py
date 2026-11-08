"""Availability boundaries for real empirical computations, without mocks."""

from __future__ import annotations

import json

import numpy as np
import pytest

from beestack.brain.empirical import CalciumImagingProtocol, summarize_calcium_trials
from beestack.brain.empirical_analysis import (
    DataQualityCheck,
    EmpiricalTemplateBank,
    activity_summary_from_components,
    all_checks_passed,
    analyze_odor_panel,
)
from beestack.brain.empirical_data import (
    EmpiricalOdorResponsePanel,
    antennal_vibration_from_movement,
    summarize_antennal_movement_rows,
    summarize_waggle_follower_rows,
    waggle_vibration_from_followers,
)


def _bank(*vectors: tuple[float, ...]) -> EmpiricalTemplateBank:
    return EmpiricalTemplateBank(
        templates={str(index): np.array(vector) for index, vector in enumerate(vectors)},
        sources={str(index): ("deterministic-test",) for index in range(len(vectors))},
        quality_checks=(),
    )


def test_empty_activity_serializes_null_with_zero_counts() -> None:
    summary = activity_summary_from_components((), (), _bank())
    payload = json.loads(json.dumps(summary.as_dict(), allow_nan=False))
    for key in (
        "mean_odor_separability",
        "calcium_mean_latency_s",
        "calcium_inhibitory_fraction",
        "calcium_excitatory_fraction",
        "aftersmell_response_mean",
        "all_quality_checks_passed",
    ):
        assert payload[key] is None
    for key in (
        "quality_check_count",
        "odor_separability_pair_count",
        "calcium_latency_observation_count",
        "calcium_inhibitory_observation_count",
        "calcium_excitatory_observation_count",
        "aftersmell_observation_count",
    ):
        assert payload[key] == 0
    assert payload["antennal_active_sensing_drive"] == {
        "odor_on_fraction": None,
        "theta_derivative_drive": None,
        "left_right_synchrony": None,
    }
    assert payload["neuromodulatory_defence_summary"]["mean_abs_response"] is None
    assert payload["region_response_means"] == {}


@pytest.mark.parametrize(
    ("vectors", "expected", "pairs"),
    [
        ((), None, 0),
        (((1.0, 0.0),), None, 0),
        (((1.0, 0.0), (1.0, 0.0)), 0.0, 1),
        (((1.0, 0.0), (0.0, 1.0)), 1.0, 1),
        (((1.0, 0.0), (-1.0, 0.0)), 1.0, 1),
        (((1.0, 0.0), (1.0, 0.0), (0.0, 1.0)), 2.0 / 3.0, 3),
        (((0.0, 0.0), (0.0, 0.0)), None, 0),
        (((0.0, 0.0), (1.0, 0.0)), None, 0),
        (((0.0, 0.0), (1.0, 0.0), (1.0, 0.0)), 0.0, 1),
        (((float("nan"), 0.0), (1.0, 0.0)), None, 0),
        (((float("inf"), 0.0), (1.0, 0.0), (1.0, 0.0)), 0.0, 1),
    ],
)
def test_odor_separability_preserves_cosine_complement(
    vectors: tuple[tuple[float, ...], ...], expected: float | None, pairs: int
) -> None:
    summary = activity_summary_from_components((), (), _bank(*vectors))
    if expected is None:
        assert summary.mean_odor_separability is None
    else:
        assert summary.mean_odor_separability == pytest.approx(expected)
    assert summary.odor_separability_pair_count == pairs


def test_calcium_and_aftersmell_observed_zero_are_not_missing() -> None:
    protocol = CalciumImagingProtocol(
        acquisition_hz=1.0,
        baseline_s=1.0,
        stimulus_s=(0.0, 2.0),
        odorant_count=1,
        trial_count=1,
        bee_count=1,
        glomeruli_tracked=2,
        source_dataset_id="constant-fluorescence",
    )
    calcium = summarize_calcium_trials(np.ones((1, 1, 1, 3, 2)), protocol)
    panel = EmpiricalOdorResponsePanel(
        dataset_id="zero-post-odor",
        response_matrix=np.zeros((2, 2)),
        stimulus_labels=("a", "b"),
        channel_labels=("left", "right"),
        modality="post-odor timecourse",
        units="response",
    )
    summary = activity_summary_from_components(
        (panel,), (analyze_odor_panel(panel),), _bank(), calcium_summaries=(calcium,)
    )
    payload = json.loads(json.dumps(summary.as_dict(), allow_nan=False))
    for key in (
        "calcium_mean_latency_s",
        "calcium_inhibitory_fraction",
        "calcium_excitatory_fraction",
        "aftersmell_response_mean",
    ):
        assert payload[key] == 0.0
    for key in (
        "calcium_latency_observation_count",
        "calcium_inhibitory_observation_count",
        "calcium_excitatory_observation_count",
        "aftersmell_observation_count",
    ):
        assert payload[key] == 1
    assert summary.quality_check_count == 4
    assert summary.all_quality_checks_passed is False
    assert summary.region_response_means == {"whole_brain_or_other": 0.0}


def test_derivative_absence_and_measured_zero_have_distinct_counts() -> None:
    absent = summarize_antennal_movement_rows([{"Odor_detector": "Off"}])
    zero = summarize_antennal_movement_rows(
        [
            {"deriv1LeftTheta": 0.0, "deriv1RightTheta": "NA"},
            {"deriv1LeftTheta": float("nan"), "deriv1RightTheta": 0.0},
        ]
    )
    observed = summarize_antennal_movement_rows(
        [{"deriv1LeftTheta": -2.0, "deriv1RightTheta": 4.0}]
    )
    assert absent.mean_abs_theta_derivative is None
    assert absent.theta_derivative_observation_count == 0
    assert zero.mean_abs_theta_derivative == 0.0
    assert zero.theta_derivative_observation_count == 2
    assert observed.mean_abs_theta_derivative == 3.0
    assert observed.theta_derivative_observation_count == 2
    for movement, expected in ((absent, None), (zero, 0.0)):
        summary = activity_summary_from_components((), (), _bank(), antennal_summaries=(movement,))
        payload = json.loads(json.dumps(summary.as_dict(), allow_nan=False))
        assert payload["antennal_active_sensing_drive"]["theta_derivative_drive"] == expected
        assert antennal_vibration_from_movement(movement)[0] == 0.0
    assert antennal_vibration_from_movement(observed)[0] == pytest.approx(3.0 / 25.0)
    assert (
        json.loads(json.dumps(absent.as_dict(), allow_nan=False))["mean_abs_theta_derivative"]
        is None
    )


@pytest.mark.parametrize(
    ("rows", "expected", "pairs"),
    [
        ([{"LeftTheta": 0.0}], None, 0),
        ([{"LeftTheta": 0.0, "RightTheta": 0.0}], None, 1),
        ([{"LeftTheta": 0.0, "RightTheta": x} for x in (0.0, 1.0)], None, 2),
        ([{"LeftTheta": x, "RightTheta": 0.0} for x in (0.0, 1.0)], None, 2),
        (
            [{"LeftTheta": x, "RightTheta": y} for x, y in ((-1.0, 1.0), (0.0, -2.0), (1.0, 1.0))],
            0.0,
            3,
        ),
        ([{"LeftTheta": x, "RightTheta": -x} for x in (-1.0, 0.0, 1.0)], -1.0, 3),
    ],
)
def test_correlation_requires_paired_nonconstant_observations(
    rows: list[dict[str, float]], expected: float | None, pairs: int
) -> None:
    movement = summarize_antennal_movement_rows(rows)
    payload = json.loads(json.dumps(movement.as_dict(), allow_nan=False))
    assert payload["paired_theta_observation_count"] == pairs
    if expected is None:
        assert payload["left_right_theta_correlation"] is None
    else:
        assert payload["left_right_theta_correlation"] == pytest.approx(expected)
    summary = activity_summary_from_components((), (), _bank(), antennal_summaries=(movement,))
    synchrony = summary.antennal_active_sensing_drive["left_right_synchrony"]
    if expected is None:
        assert synchrony is None
    else:
        assert synchrony == pytest.approx((expected + 1.0) / 2.0)


def test_quality_check_absence_is_not_a_pass() -> None:
    passed = DataQualityCheck("finite", True, 1, 1, "finite observations")
    failed = DataQualityCheck("finite", False, 0, 1, "no finite observations")
    assert all_checks_passed(()) is None
    assert all_checks_passed((passed,)) is True
    assert all_checks_passed((passed, failed)) is False
    summary = activity_summary_from_components((), (), _bank(), quality_checks=(passed,))
    assert summary.all_quality_checks_passed is True
    assert summary.quality_check_count == 1


def test_sparse_waggle_rows_preserve_unreported_statistics_and_observed_zero() -> None:
    dataset = summarize_waggle_follower_rows([{"bee_id": "follower", "angle_to_dancer_deg": 0.0}])
    payload = json.loads(json.dumps(dataset.as_dict(), allow_nan=False))
    summary = payload["summary"]
    assert summary["mean_angle_to_dancer_deg"] == 0.0
    assert summary["observation_counts"]["mean_angle_to_dancer_deg"] == 1
    for key in (
        "frame_min",
        "frame_max",
        "mean_dancer_angle_to_gravity_deg",
        "mean_left_antenna_deg",
        "mean_right_antenna_deg",
        "mean_antenna_midpoint_deg",
        "mean_scape_angle_deg",
        "follower_angle_midpoint_correlation",
        "left_right_antenna_synchrony",
        "straightness_mean",
    ):
        assert summary[key] is None
    assert summary["observation_counts"]["frame"] == 0
    assert summary["observation_counts"]["mean_left_antenna_deg"] == 0
    assert summary["observation_counts"]["follower_angle_midpoint_correlation"] == 0
    assert summary["follower_angle_midpoint_source"] is None
    assert payload["tracks"][0]["frame_min"] is None
    assert payload["tracks"][0]["mean_left_antenna_deg"] is None
    assert waggle_vibration_from_followers(dataset.summary)[0] == 0.0


@pytest.mark.parametrize(
    ("pairs", "expected"),
    [
        (((0.0, 0.0),), None),
        (((0.0, 0.0), (0.0, 1.0)), None),
        (((-1.0, 1.0), (0.0, -2.0), (1.0, 1.0)), 0.0),
        (((-1.0, 1.0), (0.0, 0.0), (1.0, -1.0)), -1.0),
    ],
)
def test_waggle_correlations_require_paired_nonconstant_observations(
    pairs: tuple[tuple[float, float], ...], expected: float | None
) -> None:
    summary = summarize_waggle_follower_rows(
        [
            {
                "bee_id": "follower",
                "frame": index,
                "angle_to_dancer_deg": angle,
                "antenna_midpoint_deg": midpoint,
                "l_antenna_deg": angle,
                "r_antenna_deg": -midpoint,
            }
            for index, (angle, midpoint) in enumerate(pairs)
        ],
        straightness_rows=[{"straightness": 0.0}],
    ).summary
    assert summary.observation_counts["follower_angle_midpoint_correlation"] == len(pairs)
    assert summary.observation_counts["left_right_antenna_synchrony"] == len(pairs)
    assert summary.observation_counts["frame"] == len(pairs)
    assert summary.frame_min == 0
    assert summary.straightness_mean == 0.0
    assert summary.observation_counts["straightness_mean"] == 1
    assert summary.follower_angle_midpoint_source == "feature_rows"
    if expected is None:
        assert summary.follower_angle_midpoint_correlation is None
        assert summary.left_right_antenna_synchrony is None
    else:
        assert summary.follower_angle_midpoint_correlation == pytest.approx(expected)
        assert summary.left_right_antenna_synchrony == pytest.approx(expected)


def test_waggle_binned_correlation_reports_its_actual_support() -> None:
    summary = summarize_waggle_follower_rows(
        [{"bee_id": "follower", "angle_to_dancer_deg": 0.0, "antenna_midpoint_deg": 0.0}],
        binned_rows=[
            {"midpt_mean_deg": value, "bin_idx_of_angle_to_dancer_deg": value}
            for value in (-1.0, 0.0, 1.0)
        ],
    ).summary
    assert summary.follower_angle_midpoint_correlation == pytest.approx(1.0)
    assert summary.follower_angle_midpoint_source == "binned_rows"
    assert summary.observation_counts["follower_angle_midpoint_correlation"] == 3
    assert summary.feature_row_count == 1


def test_waggle_error_degradation_is_not_clipped_to_one_hundred_percent() -> None:
    summary = summarize_waggle_follower_rows(
        [{"bee_id": "follower", "angle_to_dancer_deg": 0.0}],
        model_error_rows=[
            {"_source_file": "no_antennae.csv", "vector_error_deg": 1.0},
            {"_source_file": "both_antennae.csv", "vector_error_deg": 3.0},
        ],
    ).summary
    assert summary.decoding_improvement_fraction == -2.0
    assert summary.no_antennae_error_count == summary.both_antennae_error_count == 1
    assert summary.confidence_score == 0.0
    assert waggle_vibration_from_followers(summary)[0] == 0.0


@pytest.mark.parametrize(
    "errors",
    [
        [
            {"_source_file": "no_antennae.csv", "vector_error_deg": 1e-320},
            {"_source_file": "both_antennae.csv", "vector_error_deg": 1.0},
        ],
        [{"mean_rad": 1e308}],
    ],
)
def test_waggle_unrepresentable_derived_errors_fail_explicitly(errors) -> None:
    with pytest.raises(ValueError):
        summarize_waggle_follower_rows(
            [{"bee_id": "follower", "angle_to_dancer_deg": 0.0}],
            model_error_rows=errors,
        )


def test_waggle_absolute_error_means_do_not_overflow_representable_results() -> None:
    summary = summarize_waggle_follower_rows(
        [{"bee_id": "follower", "angle_to_dancer_deg": 0.0}],
        model_error_rows=[
            {"_source_file": f"{condition}.csv", "vector_error_deg": 1e308}
            for condition in ("no_antennae", "both_antennae")
            for _ in range(2)
        ],
    ).summary
    assert summary.mean_abs_vector_error_deg == 1e308
    assert summary.no_antennae_mean_abs_error_deg == 1e308
    assert summary.both_antennae_mean_abs_error_deg == 1e308
    assert summary.decoding_improvement_fraction == 0.0
    assert summary.model_error_row_count == 4
    assert summary.no_antennae_error_count == summary.both_antennae_error_count == 2
    json.dumps(summary.as_dict(), allow_nan=False)
