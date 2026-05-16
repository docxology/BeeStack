"""Real-data coverage for research.synthesis validation/edge branches (no mocks)."""

from __future__ import annotations

import math

import pytest

from beestack.research.synthesis import (
    ModuleSynthesisPanel,
    _float_from_nested,
    _signposting_fraction,
    _simulation_time_series_statistics,
    _validate_metric_map,
)


def _panel(**over: object) -> ModuleSynthesisPanel:
    base = dict(
        module="BeeBody",
        fidelity_level="reduced",
        validation_fraction=0.5,
        metric_count=1,
        evidence_count=1,
        known_gap_count=1,
        artifact_count=1,
        log_metric_mean=0.0,
        readiness_score=0.5,
    )
    base.update(over)
    return ModuleSynthesisPanel(**base)  # type: ignore[arg-type]


def test_module_synthesis_panel_validation_raises() -> None:
    assert _panel().module == "BeeBody"  # valid baseline
    with pytest.raises(ValueError, match="unknown synthesis module"):
        _panel(module="BeeWrong")
    with pytest.raises(ValueError, match="fidelity_level must be nonempty"):
        _panel(fidelity_level="")
    with pytest.raises(ValueError, match="must be finite"):
        _panel(log_metric_mean=math.inf)
    with pytest.raises(ValueError, match=r"validation_fraction must be in \[0, 1\]"):
        _panel(validation_fraction=1.5)
    with pytest.raises(ValueError, match=r"readiness_score must be in \[0, 1\]"):
        _panel(readiness_score=-0.1)
    with pytest.raises(ValueError, match="metric_count must be nonnegative"):
        _panel(metric_count=-1)


def test_signposting_fraction_branches() -> None:
    # total <= 0 -> 0.0
    assert _signposting_fraction({}, {}) == 0.0
    # union (not max) of distinct dirs each missing a different file
    frac = _signposting_fraction(
        {
            "directory_count": 4,
            "missing_readme_dirs": ("a", "b"),
            "missing_agents_dirs": ("b", "c"),
        },
        {},
    )
    assert frac == pytest.approx((4 - 3) / 4)  # union {a,b,c} = 3 missing
    # readiness fallback for directory_count, nothing missing -> 1.0
    assert _signposting_fraction({}, {"signposting": {"directory_count": 2}}) == 1.0


def test_validate_metric_map_raises() -> None:
    _validate_metric_map({"a": 1.0}, "x")  # valid: no raise
    with pytest.raises(ValueError, match="must not be empty"):
        _validate_metric_map({}, "x")
    with pytest.raises(ValueError, match="keys must be nonempty"):
        _validate_metric_map({"": 1.0}, "x")
    with pytest.raises(ValueError, match="must be finite numbers"):
        _validate_metric_map({"a": math.inf}, "x")
    with pytest.raises(ValueError, match="must be finite numbers"):
        _validate_metric_map({"a": "z"}, "x")  # type: ignore[dict-item]


def test_simulation_time_series_statistics_empty_records() -> None:
    out = _simulation_time_series_statistics(
        (), {"steps": 7, "total_recruited_followers": 3, "mean_wing_power_mw": 1.5}
    )
    assert out == {
        "simulation_step_count": 7.0,
        "simulation_energy_drop_j": 0.0,
        "simulation_thermal_error_improvement_c": 0.0,
        "simulation_policy_switch_count": 0.0,
        "simulation_recruited_total": 3.0,
        "simulation_mean_wing_power_mw": 1.5,
    }


def test_simulation_time_series_statistics_with_records() -> None:
    records = (
        {
            "energy_j": 1.0,
            "wing_power_mw": 2.0,
            "selected_policy": "scout",
            "recruited_followers": 1,
        },
        {
            "energy_j": 0.4,
            "wing_power_mw": 4.0,
            "selected_policy": "rest",
            "recruited_followers": 2,
        },
    )
    out = _simulation_time_series_statistics(records, {})
    assert out["simulation_step_count"] == 2.0
    assert out["simulation_energy_drop_j"] == pytest.approx(0.6)
    assert out["simulation_policy_switch_count"] == 1.0
    assert out["simulation_recruited_total"] == 3.0
    assert out["simulation_mean_wing_power_mw"] == pytest.approx(3.0)


def test_float_from_nested_default_branch() -> None:
    payload = {"module_panels": [{"module": "BeeBrain", "quantitative_metrics": {"f": "bad"}}]}
    assert (
        _float_from_nested(
            payload,
            ("module_panels", "BeeBrain", "quantitative_metrics", "f"),
            default=0.0,
        )
        == 0.0
    )
    assert _float_from_nested({}, ("nope",), default=2.5) == 2.5
