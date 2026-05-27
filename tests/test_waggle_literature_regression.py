"""Tests for waggle communication literature regression report."""

from __future__ import annotations

import json
from pathlib import Path

from beestack.config import BeeStackConfig
from beestack.waggle_literature_regression import (
    build_waggle_literature_regression_report,
    write_waggle_literature_regression_report,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_waggle_literature_regression_report_passes_with_current_artifacts() -> None:
    report = build_waggle_literature_regression_report(PROJECT_ROOT, BeeStackConfig())
    assert report.checks
    assert report.passed
    assert "hadjitofi2024figshare" in report.literature_anchors


def test_write_waggle_literature_regression_report_creates_json() -> None:
    path = write_waggle_literature_regression_report(PROJECT_ROOT, BeeStackConfig())
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema"] == "beestack.waggle_literature_regression.v1"
    assert payload["passed"] is True
