from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from openpyxl import Workbook

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


@pytest.fixture
def odor_fixture_project(tmp_path: Path):
    """Synthetic numeric XLSX in an isolated project; never a biological payload."""

    from beestack.config import config_from_mapping

    root = tmp_path / "isolated_project"
    config = {"seed": 7, "brain": {"kenyon_cells_per_hemisphere": 100}}
    canonical = root / "docs/manuscript"
    canonical.mkdir(parents=True)
    (canonical / "config.yaml").write_text(json.dumps({"beestack": config}), encoding="utf-8")
    files = root / "output/data/empirical_sources/synthetic-test-odor-panel/files"
    files.mkdir(parents=True)
    workbook = Workbook()
    sheet = workbook.active
    for row in (
        ("stimulus", "g1", "g2"),
        ("hexanal", 1.0, 3.0),
        ("hexanal", 3.0, 5.0),
        ("octanol", 2.0, 0.0),
        ("octanol", 4.0, 2.0),
    ):
        sheet.append(row)
    workbook.save(files / "synthetic_odor_fixture.xlsx")
    workbook.close()
    return root, config_from_mapping(config)
