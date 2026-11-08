"""Missing empirical data cannot force or certify retained manuscript figures."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from beestack.figure_audit import audit_figures
from beestack.pipeline import run_empirical_analysis
from beestack.visualization.figure_registry import high_priority_figure_artifacts


def test_empirical_primary_requirements_follow_current_raw_bound_analysis(odor_fixture_project):
    root, cfg = odor_fixture_project
    primary = high_priority_figure_artifacts()
    empirical = {path for path in primary if path.startswith("output/figures/empirical/")}
    core = next(path for path in primary if path not in empirical)
    before = audit_figures(root)
    assert empirical.isdisjoint(before.missing_high_priority_artifacts)
    assert core in before.missing_high_priority_artifacts
    assert run_empirical_analysis(cfg, root)
    current = audit_figures(root)
    assert empirical.issubset(current.missing_high_priority_artifacts)
    assert core in current.missing_high_priority_artifacts
    raw = next((root / "output/data/empirical_sources").rglob("*.xlsx"))
    with raw.open("ab") as handle:
        handle.write(b"changed input bytes")
    stale = audit_figures(root)
    assert empirical.isdisjoint(stale.missing_high_priority_artifacts)
    assert core in stale.missing_high_priority_artifacts


def test_retained_empirical_image_is_forbidden_without_current_analysis(tmp_path: Path):
    manuscript = tmp_path / "output/manuscript"
    manuscript.mkdir(parents=True)
    image = tmp_path / "output/figures/empirical/retained.png"
    image.parent.mkdir(parents=True)
    Image.new("RGB", (10, 10), "red").save(image)
    (manuscript / "00_section.md").write_text(
        "![Retained illustration](../figures/empirical/retained.png) {#fig:retained}\n"
    )
    audit = audit_figures(tmp_path, required_primary_artifacts=())
    assert audit.unavailable_empirical_references
    assert not audit.passed
