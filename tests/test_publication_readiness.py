"""Tests for BeeStack publication readiness gate."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from beestack.publication_readiness import check_publication_readiness
from beestack.version import PACKAGE_VERSION


def test_publication_readiness_blocks_wrong_manuscript_version(tmp_path: Path) -> None:
    manuscript = tmp_path / "docs" / "manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "config.yaml").write_text(
        yaml.safe_dump({"paper": {"version": "0.9"}, "publication": {"doi": ""}}),
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nversion = "{PACKAGE_VERSION}"\n',
        encoding="utf-8",
    )
    pdf_dir = tmp_path / "output" / "pdf"
    pdf_dir.mkdir(parents=True)
    (pdf_dir / "BeeStack_combined.pdf").write_bytes(b"%PDF-1.4\n")
    data_dir = tmp_path / "output" / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "manuscript_variables.json").write_text(
        json.dumps({"TITLE": "BeeStack"}) + "\n",
        encoding="utf-8",
    )
    (data_dir / "brain_data_completeness.json").write_text(
        json.dumps({"parseability_target_satisfied": False, "parseable_fraction": 0.6}) + "\n",
        encoding="utf-8",
    )

    result = check_publication_readiness(tmp_path)

    assert result["ok"] is False
    assert any("paper.version" in blocker for blocker in result["blockers"])
