"""Real generation coverage for visualization.figures + sidecars (no mocks)."""

from __future__ import annotations

from pathlib import Path

from beestack.visualization.figures import generate_analysis_figures


def _records() -> list[dict[str, object]]:
    return [
        {
            "step_index": i,
            "energy_j": 1.0 - 0.1 * i,
            "comb_fraction": 0.1 + 0.02 * i,
            "body_speed_m_s": 0.05 + 0.01 * i,
            "wing_power_mw": 40.0 + i,
            "dominant_empirical_alignment": 0.3 + 0.05 * i,
            "dominant_empirical_odor": "1-octanol",
            "selected_policy": "scout" if i % 2 else "nurse_brood",
            "recruited_followers": i,
            "mean_pheromone": 0.2 + 0.01 * i,
            "brood_temperature_error_c": 2.5 - 0.1 * i,
        }
        for i in range(6)
    ]


def test_generate_analysis_figures_writes_pngs_and_sidecars(tmp_path: Path) -> None:
    modules = ["BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"]
    paths = generate_analysis_figures(_records(), modules, tmp_path)
    assert len(paths) == 12
    for p in paths:
        assert p.exists(), f"missing figure {p}"
        assert p.stat().st_size > 0
        sidecar = p.with_suffix(".json")
        assert sidecar.exists(), f"missing sidecar for {p}"
        assert sidecar.stat().st_size > 0


def test_generate_analysis_figures_empty_records(tmp_path: Path) -> None:
    # Degenerate input must still produce valid non-empty figures (defensive
    # series helpers return [default]).
    paths = generate_analysis_figures([], [], tmp_path)
    assert len(paths) == 12
    assert all(p.exists() and p.stat().st_size > 0 for p in paths)
