"""Behavioral regressions for finite numerical observations and population counts."""

import math
from dataclasses import replace
from fractions import Fraction

import numpy as np
import pytest

from beestack.brain.datasets import empirical_brain_datasets
from beestack.brain.empirical import (
    CalciumImagingProtocol,
    empirical_alignment_score,
    negative_delta_f_over_f,
    summarize_calcium_trials,
)
from beestack.brain.empirical_analysis import (
    EmpiricalTemplateBank,
    activity_summary_from_components,
    bee_brain_data_completeness_panel,
    validate_calcium_dataset,
)
from beestack.brain.empirical_data import calcium_dataset_from_trial_array
from beestack.brain.mushroom_body import kc_class_counts, kenyon_sparse_code
from beestack.brain.pipeline import process_observation
from beestack.brain.state import KenyonProjection
from beestack.brain.waggle import decode_waggle, waggle_kinematics_from_config
from beestack.config import BeeStackConfig, config_from_mapping
from beestack.contracts import zero_observation
from beestack.swarm.metrics import colony_expected_free_energy


def _protocol() -> CalciumImagingProtocol:
    return CalciumImagingProtocol(10.0, 1.0, (1.0, 2.0), 1, 1, 1, 3, "measured-calcium")


def test_calcium_summary_rejects_nan_baseline_that_passes_quality_screen() -> None:
    traces = np.ones((1, 1, 1, 100, 1))
    traces[..., 10:20, :] = 2.0
    traces[..., 0, :] = np.nan
    dataset = calcium_dataset_from_trial_array("nan-baseline", traces, 10.0, ("odor",))
    assert all(check.passed for check in validate_calcium_dataset(dataset))
    with pytest.raises(ValueError, match="complete finite traces"):
        summarize_calcium_trials(dataset.traces, dataset.protocol(BeeStackConfig()))


@pytest.mark.parametrize("invalid", [math.nan, math.inf, -math.inf])
@pytest.mark.parametrize("frame", [0, 15, 99])
def test_calcium_summary_rejects_nonfinite_traces(invalid: float, frame: int) -> None:
    traces = np.ones((1, 1, 1, 100, 3))
    traces[..., frame, 0] = invalid
    with pytest.raises(ValueError, match="finite traces"):
        summarize_calcium_trials(traces, _protocol())


@pytest.mark.parametrize("shape", [(0, 100, 3), (1, 100, 0)])
def test_calcium_summary_rejects_empty_observation_axes(shape: tuple[int, ...]) -> None:
    with pytest.raises(ValueError, match="finite traces"):
        summarize_calcium_trials(np.ones(shape), _protocol())


def test_calcium_summary_preserves_measured_zero_and_response_signs() -> None:
    traces = np.ones((1, 1, 1, 100, 3))
    zero = summarize_calcium_trials(traces, _protocol())
    np.testing.assert_array_equal(zero.mean_response, np.zeros(3))
    assert zero.excitatory_fraction == zero.inhibitory_fraction == 0.0
    activity = activity_summary_from_components(
        (), (), EmpiricalTemplateBank({}, {}, ()), calcium_summaries=(zero,)
    )
    assert activity.calcium_mean_latency_s == 1.0
    assert activity.calcium_inhibitory_fraction == activity.calcium_excitatory_fraction == 0.0
    assert activity.calcium_latency_observation_count == 1
    assert activity.calcium_inhibitory_observation_count == 1
    assert activity.calcium_excitatory_observation_count == 1
    traces[..., 10:20, 0] = 1.4
    traces[..., 10:20, 1] = 0.7
    summary = summarize_calcium_trials(traces, _protocol())
    np.testing.assert_allclose(summary.mean_response, [-0.4, 0.3, 0.0])
    assert summary.excitatory_fraction == pytest.approx(1 / 3)
    assert summary.inhibitory_fraction == pytest.approx(1 / 3)


def test_calcium_normalization_rejects_nonfinite_derived_results() -> None:
    with pytest.raises(ValueError, match="baseline fluorescence must be finite"):
        negative_delta_f_over_f(np.full((10, 1), 1e308), 10)
    traces = np.array([[0.1], [1e308]])
    with pytest.raises(ValueError, match="normalized calcium responses must be finite"):
        negative_delta_f_over_f(traces, 1)
    traces = np.ones((1, 1, 1, 100, 3))
    traces[..., 10:20, :] = 1e308
    with pytest.raises(ValueError, match="response means must be finite"):
        summarize_calcium_trials(traces, _protocol())


@pytest.mark.parametrize("rate", [0.0, -1.0, math.nan, math.inf])
def test_calcium_summary_rejects_invalid_sampling_rate(rate: float) -> None:
    with pytest.raises(ValueError, match="acquisition_hz"):
        summarize_calcium_trials(np.ones((100, 3)), replace(_protocol(), acquisition_hz=rate))


@pytest.mark.parametrize(
    ("values", "weights", "expected"),
    [
        ([1e308, 1e308], [2.0, 2.0], 1e308),
        ([1.0, 1.0], [1e308, 1e308], 1.0),
        ([1e-308, 1e-308], [1e-308, 1e-308], 1e-308),
        ([1e308, -1e308], [1.0, 1.0], 0.0),
        ([0.0, 0.0], [1e308, 1e308], 0.0),
        ([1e308, 0.0], [0.0, 1.0], 0.0),
        ([1e308, 1e-308], [1e-308, 1e308], 2e-308),
        ([1.0, 3.0], [-1.0, 2.0], 5.0),
        ([1.0, 1.0, 1.0], [1e308, -1e308, 1e-308], 1.0),
    ],
)
def test_colony_efe_retains_representable_extreme_means(values, weights, expected) -> None:
    result = colony_expected_free_energy(np.array(values), np.array(weights))
    assert math.isfinite(result)
    assert result == pytest.approx(expected, rel=1e-14, abs=0.0)


@pytest.mark.parametrize("cancel_weights", [False, True])
def test_colony_efe_preserves_adjacent_float_cancellation(cancel_weights: bool) -> None:
    large = 1e308
    adjacent = float(np.nextafter(large, 0.0))
    values = np.array([1.0, 2.0]) if cancel_weights else np.array([large, -adjacent])
    weights = np.array([large, -adjacent]) if cancel_weights else np.ones(2)
    expected = float(
        sum(
            Fraction(float(value)) * Fraction(float(weight))
            for value, weight in zip(values, weights, strict=True)
        )
        / sum(Fraction(float(weight)) for weight in weights)
    )
    assert colony_expected_free_energy(values, weights) == pytest.approx(
        expected, rel=2e-15, abs=0.0
    )


def test_colony_efe_preserves_residual_from_cancelling_rounded_products() -> None:
    result = colony_expected_free_energy(
        np.array([134217729.0, -134217728.0]), np.array([134217727.0, 134217728.0])
    )
    assert result == float(Fraction(-1, 268435455))


def test_colony_efe_reconstructs_subnormal_mean_without_double_rounding() -> None:
    minimum = float.fromhex("0x0.0000000000001p-1022")
    weights = np.array([1.5, np.nextafter(1.5, 0.0)])
    exact = (
        Fraction(minimum)
        * Fraction(float(weights[0]))
        / sum(Fraction(float(weight)) for weight in weights)
    )
    assert float(exact) == minimum
    assert colony_expected_free_energy(np.array([minimum, 0.0]), weights) == float(exact)


def test_colony_efe_preserves_matrix_scalar_and_penalty_semantics() -> None:
    assert colony_expected_free_energy(
        np.array([[1.0, 2.0], [3.0, 4.0]]),
        np.array([[1.0, 2.0], [3.0, 4.0]]),
        0.5,
    ) == pytest.approx(3.5)
    assert colony_expected_free_energy(np.array(2.0), np.array(3.0), 0.5) == 2.5
    assert colony_expected_free_energy(
        np.array([-1e308, 0.0]), np.array([2.0, -1.0]), 1e308
    ) == pytest.approx(-1e308)


@pytest.mark.parametrize(
    ("values", "weights", "penalty"),
    [([1e308, 0.0], [2.0, -1.0], 0.0), ([1e308], [1.0], 1e308)],
)
def test_colony_efe_explicitly_rejects_unrepresentable_output(values, weights, penalty) -> None:
    with pytest.raises(ValueError, match="representable.*finite"):
        colony_expected_free_energy(np.array(values), np.array(weights), penalty)


@pytest.mark.parametrize("scale", [1e-308, 1e-200, 1.0, 1e200, 1e308])
def test_cosine_is_invariant_to_finite_nonzero_magnitude(scale: float) -> None:
    vector = np.array([1.0, -0.5, 0.0])
    assert empirical_alignment_score(vector, vector * scale) == pytest.approx(1.0)
    assert empirical_alignment_score(vector * scale, vector * scale) == pytest.approx(1.0)
    assert empirical_alignment_score(vector, -vector * scale) == pytest.approx(-1.0)
    assert empirical_alignment_score(np.array([0.0, 1.0]), np.array([scale, 0.0])) == 0.0
    assert empirical_alignment_score(np.zeros(3), vector * scale) == 0.0


@pytest.mark.parametrize("invalid", [math.nan, math.inf, -math.inf])
def test_cosine_rejects_nonfinite_even_opposite_zero_vector(invalid: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        empirical_alignment_score(np.zeros(1), np.array([invalid]))
    with pytest.raises(ValueError, match="finite"):
        empirical_alignment_score(np.array([invalid]), np.ones(1))


@pytest.mark.parametrize("scale", [1e-200, 1e200, 1e308])
def test_process_observation_uses_scale_invariant_empirical_alignment(scale: float) -> None:
    cfg = config_from_mapping({"brain": {"kenyon_cells_per_hemisphere": 100}})
    channels = np.zeros(cfg.body.olfactory_channels)
    channels[0] = 1.0
    observation = replace(zero_observation(cfg), antennal_channels=channels)
    template = np.zeros(cfg.brain.glomeruli)
    template[0] = scale
    brain = process_observation(observation, cfg, seed=7, odor_templates={"measured": template})
    assert brain.empirical_alignment["measured"] == pytest.approx(1.0)
    assert process_observation(observation, cfg, seed=7).empirical_alignment == {}


def test_completeness_counts_only_target_status_population() -> None:
    target, foreign = empirical_brain_datasets()[:2]
    panel = bee_brain_data_completeness_panel(
        (target,),
        downloaded_dataset_ids=(foreign.dataset_id,),
        parseable_dataset_ids=(foreign.dataset_id,),
    )
    assert panel.dataset_count == 1
    assert not panel.source_statuses[0].downloaded
    assert not panel.source_statuses[0].parseable
    assert panel.downloaded_fraction == panel.parseable_fraction == 0.0
    assert not panel.parseability_target_satisfied
    panel = bee_brain_data_completeness_panel(
        (target,),
        downloaded_dataset_ids=(target.dataset_id, foreign.dataset_id, target.dataset_id),
        parseable_dataset_ids=(target.dataset_id, foreign.dataset_id, target.dataset_id),
    )
    assert panel.downloaded_dataset_count == sum(row.downloaded for row in panel.source_statuses)
    assert panel.parseable_dataset_count == sum(row.parseable for row in panel.source_statuses)
    assert panel.downloaded_fraction == panel.parseable_fraction == 1.0
    assert panel.parseability_target_satisfied


def test_completeness_rejects_duplicate_dataset_identity() -> None:
    dataset = empirical_brain_datasets()[0]
    conflicting = replace(dataset, source_url="https://example.org/different")
    for rows in ((dataset, dataset), (dataset, conflicting)):
        with pytest.raises(ValueError, match="duplicate dataset identity"):
            bee_brain_data_completeness_panel(rows)
    empty = bee_brain_data_completeness_panel((), downloaded_dataset_ids=(dataset.dataset_id,))
    assert empty.dataset_count == empty.downloaded_dataset_count == 0
    assert empty.downloaded_fraction == empty.parseable_fraction == 0.0
    assert not empty.parseability_target_satisfied


@pytest.mark.parametrize(("fraction", "expected"), [(0.0, 0), (0.996, 99), (1.0, 100)])
def test_kc_class_counts_match_actual_sparse_kernel_partition(
    fraction: float, expected: int
) -> None:
    cfg = config_from_mapping(
        {
            "brain": {
                "glomeruli": 2,
                "kenyon_cells_per_hemisphere": 50,
                "kc_class_i_fraction": fraction,
            },
            "empirical": {"calcium_glomeruli_tracked": 2},
        }
    )
    counts = kc_class_counts(cfg)
    assert counts["class_i"] == expected
    assert counts["class_ii"] == 100 - expected
    projection = KenyonProjection(np.zeros((100, 10), dtype=np.int64), 2, 7)
    code = kenyon_sparse_code(np.ones(2), cfg, seed=7, projection=projection)
    np.testing.assert_array_equal(
        code.activations, np.where(code.active_indices < expected, 0.5, 0.625)
    )


@pytest.mark.parametrize(
    ("angle", "sun", "drift"),
    [(1e308, 1e308, 0.0), (-1e308, -1e308, 1e308), (35.0, 120.0, 5.0)],
)
def test_waggle_normalizes_finite_operands_before_bearing_addition(angle, sun, drift) -> None:
    expected = float((Fraction(angle) + Fraction(sun) - Fraction(drift)) % 360)
    dance = decode_waggle(1.2, angle, sun, 0.8, drift)
    assert math.isfinite(dance.azimuth_deg)
    assert 0.0 <= dance.azimuth_deg < 360.0
    assert dance.azimuth_deg == pytest.approx(expected)


def test_waggle_config_accepts_finite_extreme_normalized_direction() -> None:
    cfg = config_from_mapping(
        {"visualization": {"waggle_dance_angle_deg": 1e308, "waggle_dance_sun_azimuth_deg": 1e308}}
    )
    kinematics = waggle_kinematics_from_config(cfg)
    assert kinematics.decoded_azimuth_deg == float((2 * Fraction(1e308)) % 360)
    assert 0.0 <= kinematics.decoded_azimuth_deg < 360.0


@pytest.mark.parametrize(
    "field", ["duration_s", "angle_deg", "sun_azimuth_deg", "quality_score", "drift_deg"]
)
@pytest.mark.parametrize("invalid", [math.nan, math.inf, -math.inf])
def test_waggle_rejects_nonfinite_decoder_operands(field: str, invalid: float) -> None:
    operands = dict(
        duration_s=1.0, angle_deg=35.0, sun_azimuth_deg=120.0, quality_score=0.8, drift_deg=0.0
    )
    operands[field] = invalid
    with pytest.raises(ValueError, match=f"{field} must be finite"):
        decode_waggle(**operands)


@pytest.mark.parametrize("scale", [1e-200, 1e200])
@pytest.mark.parametrize("orthogonal", [False, True])
def test_activity_separability_retains_scaled_nonzero_templates(
    scale: float, orthogonal: bool
) -> None:
    bank = EmpiricalTemplateBank(
        {
            "first": np.array([scale, 0.0]),
            "second": np.array([0.0, scale]) if orthogonal else np.array([scale, 0.0]),
            "zero": np.zeros(2),
            "undefined": np.array([math.nan, 0.0]),
        },
        {},
        (),
    )
    activity = activity_summary_from_components((), (), bank)
    assert activity.odor_separability_pair_count == 1
    assert activity.mean_odor_separability == (1.0 if orthogonal else 0.0)
    single = EmpiricalTemplateBank({"only": bank.templates["first"], "zero": np.zeros(2)}, {}, ())
    activity = activity_summary_from_components((), (), single)
    assert activity.odor_separability_pair_count == 0
    assert activity.mean_odor_separability is None


@pytest.mark.parametrize("fraction", [-0.01, 1.01])
def test_config_rejects_out_of_range_kc_class_fraction(fraction: float) -> None:
    with pytest.raises(ValueError, match="kc_class_i_fraction"):
        config_from_mapping({"brain": {"kc_class_i_fraction": fraction}})


def test_kc_public_count_matches_observed_class_ii_gain_at_fractional_boundary() -> None:
    cfg = config_from_mapping(
        {
            "brain": {
                "glomeruli": 2,
                "kenyon_cells_per_hemisphere": 100,
                "kc_class_i_fraction": 0.999,
            },
            "empirical": {"calcium_glomeruli_tracked": 2},
        }
    )
    claws = np.zeros((200, 10), dtype=np.int64)
    claws[198, :] = 1
    claws[199, :5] = 1
    projection = KenyonProjection(claws, 2, 7)
    code = kenyon_sparse_code(np.array([0.0, 1.0]), cfg, seed=7, projection=projection)
    # Cell 199 has half-maximal normalized drive, so the actual class-II
    # gain is visible rather than hidden by clipping a winning cell to one.
    np.testing.assert_array_equal(code.activations[code.active_indices == 199], [0.625])
    counts = kc_class_counts(cfg)
    assert counts["class_i"] == 199
    assert counts["class_ii"] == 1
