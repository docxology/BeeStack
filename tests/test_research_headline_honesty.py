"""Require disclosed limitations alongside a perfect configured self-test rate."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESEARCH_REPORT = PROJECT_ROOT / "output" / "data" / "research_suite_report.json"


def test_perfect_self_test_rate_requires_disclosed_gaps() -> None:
    """A 1.0 self-test rate must coexist with at least one acknowledged gap.

    Claiming every module self-test passes *and* cataloguing zero limitations
    is the over-claim state. Because the self-test rate is structurally a mean
    of config-band booleans, a perfect rate is uninformative on its own; it is
    only honest when the run still publishes its known gaps.
    """
    report = json.loads(RESEARCH_REPORT.read_text(encoding="utf-8"))
    overall = float(report["overall_validation_fraction"])
    known_gaps = report.get("known_gaps", [])
    if overall >= 1.0:
        assert len(known_gaps) > 0, (
            "overall_validation_fraction is 1.0 but the run catalogues zero "
            "known_gaps: a perfect config-band self-test rate presented with no "
            "acknowledged limitations is an over-claim. Either surface the open "
            "gaps or stop headlining the self-test rate as full validation."
        )
