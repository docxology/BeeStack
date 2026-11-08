"""Real artifact-bound regression checks; no dependence on a historical checkout."""

from __future__ import annotations

import json
from pathlib import Path

from beestack.config import BeeStackConfig
from beestack.waggle_literature_regression import build_waggle_literature_regression_report


def _artifacts(
    root: Path, *, error: float = 35.0, confidence: float = 0.65, both_error: float | None = 10.0
) -> None:
    data = root / "output/data"
    data.mkdir(parents=True)
    source = data / "empirical_sources/figshare-hadjitofi-2024-waggle-following/files"
    source.mkdir(parents=True)
    # Closed synthetic CSV fixtures exercise actual ingestion, not cached summaries.
    (source / "features.csv").write_text(
        "bee_id,frame,angle_to_dancer_deg\na,0,10\na,1,20\nb,0,30\nb,1,40\n",
        encoding="utf-8",
    )
    (source / "errors_no_antennae.csv").write_text("vector_error_deg\n20\n", encoding="utf-8")
    if both_error is not None:
        (source / "errors_both_antennae.csv").write_text(
            f"vector_error_deg\n{both_error}\n", encoding="utf-8"
        )
    metrics = {
        "waggle_follower_orientation_error_deg": error,
        "waggle_follower_orientation_confidence": confidence,
    }
    (data / "methods_analysis.json").write_text(
        json.dumps({"module_panels": [{"module": "BeeSwarm", "quantitative_metrics": metrics}]}),
        encoding="utf-8",
    )


def test_configured_orientation_boundaries_are_inclusive(tmp_path: Path) -> None:
    _artifacts(tmp_path)
    result = build_waggle_literature_regression_report(tmp_path, BeeStackConfig())
    assert result.passed
    assert all(check.passed for check in result.checks)


def test_real_methods_metric_schema_cannot_skip_a_failing_orientation(tmp_path: Path) -> None:
    _artifacts(tmp_path, error=36.0)
    result = build_waggle_literature_regression_report(tmp_path, BeeStackConfig())
    check = next(row for row in result.checks if row.name == "beeswarm_orientation_error_target")
    assert check.observed == 36.0
    assert not check.passed
    assert not result.passed


def test_missing_empirical_condition_is_an_unavailable_failed_comparison(tmp_path: Path) -> None:
    _artifacts(tmp_path, both_error=None)
    result = build_waggle_literature_regression_report(tmp_path, BeeStackConfig())
    check = next(
        row for row in result.checks if row.name == "hadjitofi_both_antennae_beat_no_antennae"
    )
    assert check.observed is None
    assert not check.passed
    assert not result.passed


def test_absent_artifacts_do_not_disappear_from_required_checks(tmp_path: Path) -> None:
    result = build_waggle_literature_regression_report(tmp_path, BeeStackConfig())
    assert not result.passed
    assert all(not check.passed and check.observed is None for check in result.checks)


def test_historical_positive_waggle_summary_cannot_replace_missing_raw_inputs(
    tmp_path: Path,
) -> None:
    _artifacts(tmp_path)
    source = tmp_path / "output/data/empirical_sources"
    for path in source.rglob("*.csv"):
        path.unlink()
    cached = tmp_path / "output/data/waggle_follower_analysis.json"
    cached.write_text(
        json.dumps(
            {
                "summary": {
                    "decoding_improvement_fraction": 0.5,
                    "both_antennae_mean_abs_error_deg": 10,
                    "no_antennae_mean_abs_error_deg": 20,
                    "track_count": 2,
                }
            }
        ),
        encoding="utf-8",
    )
    result = build_waggle_literature_regression_report(tmp_path, BeeStackConfig())
    assert not result.passed
    empirical_checks = [row for row in result.checks if row.name.startswith("hadjitofi_")]
    assert all(not row.passed and row.observed is None for row in empirical_checks)


def test_changed_raw_errors_override_a_retained_positive_summary(tmp_path: Path) -> None:
    _artifacts(tmp_path)
    data = tmp_path / "output/data"
    (data / "waggle_follower_analysis.json").write_text(
        json.dumps({"summary": {"decoding_improvement_fraction": 0.5}}), encoding="utf-8"
    )
    errors = (
        data
        / "empirical_sources/figshare-hadjitofi-2024-waggle-following/files/errors_both_antennae.csv"
    )
    errors.write_text("vector_error_deg\n40\n", encoding="utf-8")
    result = build_waggle_literature_regression_report(tmp_path, BeeStackConfig())
    check = next(
        row for row in result.checks if row.name == "hadjitofi_antenna_decoding_improvement"
    )
    assert check.observed == -1.0
    assert not check.passed
