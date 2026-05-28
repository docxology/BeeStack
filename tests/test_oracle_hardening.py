"""Iteration-11 oracle-hardening guards.

The prior publication-readiness oracle was honesty-blind: it certified ``ok:true``
while the abstract headlined a perfect validation fraction beside open gaps, and it
only shape-checked the curated DOI allowlist. These tests bind both seams.
"""

from __future__ import annotations

import json
from pathlib import Path

from beestack.publication_readiness import check_publication_readiness
from beestack.source_audit import audit_sources


def _write_research_report(root: Path, *, fraction: float, gaps: list[str]) -> None:
    data_dir = root / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "research_suite_report.json").write_text(
        json.dumps({"overall_validation_fraction": fraction, "known_gaps": gaps}) + "\n",
        encoding="utf-8",
    )


def test_gate_blocks_perfect_validation_with_zero_gaps(tmp_path: Path) -> None:
    """overall_validation_fraction>=1.0 with zero known_gaps must block release."""
    _write_research_report(tmp_path, fraction=1.0, gaps=[])

    result = check_publication_readiness(tmp_path)

    assert result["checks"]["validation_fraction_discloses_gaps"] is False
    assert result["ok"] is False
    assert any("overall_validation_fraction" in b for b in result["blockers"])


def test_gate_accepts_perfect_validation_with_disclosed_gaps(tmp_path: Path) -> None:
    """A perfect self-test rate is acceptable when the run still publishes its gaps."""
    _write_research_report(tmp_path, fraction=1.0, gaps=["calcium not yet a model input"])

    result = check_publication_readiness(tmp_path)

    assert result["checks"]["validation_fraction_discloses_gaps"] is True
    assert not any("overall_validation_fraction" in b for b in result["blockers"])


def _write_manuscript(root: Path, doi: str) -> None:
    manuscript = root / "manuscript"
    manuscript.mkdir(parents=True, exist_ok=True)
    (manuscript / "01_intro.md").write_text("A cited claim [@baddoi].\n", encoding="utf-8")
    (manuscript / "references.bib").write_text(
        "@article{baddoi,\n"
        "  title = {A Source},\n"
        "  author = {A. Author},\n"
        "  year = {2020},\n"
        f"  doi = {{{doi}}},\n"
        f"  url = {{https://doi.org/{doi}}}\n"
        "}\n",
        encoding="utf-8",
    )


def test_source_audit_flags_malformed_cited_doi(tmp_path: Path) -> None:
    """A cited entry with a non-10.NNNN/ DOI is a release blocker (not allowlist-gated)."""
    _write_manuscript(tmp_path, doi="not-a-real-doi")

    audit = audit_sources(
        tmp_path,
        required_bib_dois={},
        registry_dois=(),
        figure_registry_citation_keys=(),
        figure_registry_source_dois=(),
    )

    assert any("baddoi" in m for m in audit.malformed_cited_dois)
    assert audit.passed is False


def test_source_audit_accepts_wellformed_cited_doi(tmp_path: Path) -> None:
    """A well-formed cited DOI passes the broadened shape check."""
    _write_manuscript(tmp_path, doi="10.1234/abcd.5678")

    audit = audit_sources(
        tmp_path,
        required_bib_dois={},
        registry_dois=(),
        figure_registry_citation_keys=(),
        figure_registry_source_dois=(),
    )

    assert audit.malformed_cited_dois == ()
