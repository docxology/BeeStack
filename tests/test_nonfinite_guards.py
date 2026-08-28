"""Behavioral tests for non-finite input rejection in colony EFE and wing power.

Companion to lane(bee_methods) commit cbe7a92: the guards it added must fail
loudly on NaN/inf inputs instead of silently propagating non-finite values
into colony-level witness metrics. Real computation only, no mocks.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from beestack.body import energetics
from beestack.swarm import colony_expected_free_energy


def test_colony_efe_rejects_nonfinite_efes() -> None:
    with pytest.raises(ValueError, match="finite"):
        colony_expected_free_energy(np.array([1.0, math.nan]), np.array([1.0, 1.0]))
    with pytest.raises(ValueError, match="finite"):
        colony_expected_free_energy(np.array([1.0, math.inf]), np.array([1.0, 1.0]))


def test_colony_efe_rejects_nonfinite_weights() -> None:
    with pytest.raises(ValueError, match="finite"):
        colony_expected_free_energy(np.array([1.0, 2.0]), np.array([1.0, math.nan]))
    with pytest.raises(ValueError, match="finite"):
        colony_expected_free_energy(np.array([1.0, 2.0]), np.array([0.0, math.inf]))


def test_colony_efe_rejects_nonfinite_emergence_penalty() -> None:
    with pytest.raises(ValueError, match="finite"):
        colony_expected_free_energy(np.array([1.0]), np.array([1.0]), emergence_penalty=math.nan)
    with pytest.raises(ValueError, match="finite"):
        colony_expected_free_energy(np.array([1.0]), np.array([1.0]), emergence_penalty=math.inf)


def test_colony_efe_still_accepts_finite_inputs() -> None:
    value = colony_expected_free_energy(np.array([1.0, 3.0]), np.array([1.0, 3.0]))
    assert value == pytest.approx(2.5)
    assert math.isfinite(value)


def test_wing_power_rejects_nonfinite_inputs() -> None:
    for kwargs in (
        {"mass_mg": math.nan, "stroke_hz": 200.0},
        {"mass_mg": math.inf, "stroke_hz": 200.0},
        {"mass_mg": 80.0, "stroke_hz": math.nan},
        {"mass_mg": 80.0, "stroke_hz": 0.0},
        {"mass_mg": 80.0, "stroke_hz": 200.0, "load_fraction": math.nan},
        {"mass_mg": 80.0, "stroke_hz": 200.0, "load_fraction": math.inf},
    ):
        with pytest.raises(ValueError, match="finite"):
            energetics.wing_power_mw(**kwargs)


def test_wing_power_finite_baseline_is_in_calibrated_band() -> None:
    power = energetics.wing_power_mw(80.0, 200.0)
    assert math.isfinite(power)
    # 40-80 mW calibrated hover band for the default worker bee.
    assert 40.0 <= power <= 80.0
