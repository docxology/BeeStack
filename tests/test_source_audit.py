from __future__ import annotations

from pathlib import Path

from beestack.source_audit import (
    EXPECTED_BIB_DOIS,
    audit_sources,
    extract_pandoc_citation_keys,
    parse_bibtex_entries,
)


def test_extract_pandoc_citations_ignores_inline_code() -> None:
    text = (
        "Use `@dataclass` and `[@not_a_citation]` in code, but cite "
        "real sources [@galizia1999glomerular; @todorov2012mujoco]."
    )

    assert extract_pandoc_citation_keys(text) == (
        "galizia1999glomerular",
        "todorov2012mujoco",
    )


def test_source_audit_flags_missing_keys_and_doi_mismatches(tmp_path: Path) -> None:
    project = tmp_path
    manuscript = project / "manuscript"
    manuscript.mkdir()
    (manuscript / "01_intro.md").write_text(
        "A cited claim [@present; @missing]. A digital twin is complete.\n",
        encoding="utf-8",
    )
    (manuscript / "references.bib").write_text(
        """
@article{present,
  title = {Present Source},
  author = {A. Author},
  year = {2020},
  doi = {10.0000/wrong}
}
""",
        encoding="utf-8",
    )

    audit = audit_sources(
        project,
        required_bib_dois={"present": "10.0000/right"},
        registry_dois=(),
    )

    assert audit.passed is False
    assert "missing" in audit.missing_citation_keys
    assert audit.doi_mismatches == (
        "present: expected 10.0000/right, found 10.0000/wrong",
    )
    assert audit.unconservative_digital_twin_claims == (
        "manuscript/01_intro.md: A cited claim [@present; @missing]. A digital twin is complete.",
    )


def test_bibtex_parser_preserves_doi_and_url_fields() -> None:
    entries = parse_bibtex_entries(
        """
@article{galizia1999glomerular,
  title = {The glomerular code},
  doi = {10.1038/8144},
  url = {https://doi.org/10.1038/8144}
}
"""
    )

    assert entries["galizia1999glomerular"]["doi"] == "10.1038/8144"
    assert entries["galizia1999glomerular"]["url"] == "https://doi.org/10.1038/8144"


def test_project_source_audit_passes_current_registry_and_claim_contracts() -> None:
    audit = audit_sources(Path(__file__).resolve().parents[1])

    assert audit.passed, audit.as_dict()
    assert "10.1002/cne.20644" in audit.registry_dois_represented
    assert "10.1038/8144" in audit.registry_dois_represented
    assert not audit.figure_registry_citation_keys_missing
    assert not audit.figure_registry_source_dois_missing
    assert not audit.missing_required_bib_fields
    assert not audit.unconservative_digital_twin_claims


def test_verified_scholarship_refresh_sources_are_required_and_section_mapped() -> None:
    from beestack.source_refresh import verified_source_refresh_ledger

    required = {
        "fair4rs2022principles": "10.1038/s41597-022-01710-x",
        "riley2005flightpaths": "10.1038/nature03526",
        "landgraf2011roboticdance": "10.1371/journal.pone.0021354",
        "hateren2019neuroethology": "10.3390/insects10100336",
    }

    assert required.items() <= EXPECTED_BIB_DOIS.items()
    ledger = verified_source_refresh_ledger()
    ledger_by_key = {row.citation_key: row for row in ledger}
    assert required.keys() <= ledger_by_key.keys()
    for key, doi in required.items():
        row = ledger_by_key[key]
        assert row.direct_verification_status == "verified"
        assert row.doi == doi
        assert row.section_targets
        assert row.figure_targets
        assert row.claim_tier in {"scholarship_anchor", "method_anchor", "validation_anchor"}


def test_source_audit_flags_figure_registry_keys_and_dois_missing_from_bib(
    tmp_path: Path,
) -> None:
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    (manuscript / "01_intro.md").write_text("No bracket citations here.\n", encoding="utf-8")
    (manuscript / "references.bib").write_text(
        """
@article{wilson2017good,
  title = {Good Enough Practices},
  doi = {10.1371/journal.pcbi.1005510},
  url = {https://doi.org/10.1371/journal.pcbi.1005510}
}
""",
        encoding="utf-8",
    )

    audit = audit_sources(
        tmp_path,
        required_bib_dois={},
        registry_dois=(),
        figure_registry_citation_keys=("missing_registry_key",),
        figure_registry_source_dois=("10.0000/missing-registry-doi",),
    )

    assert audit.passed is False
    assert audit.figure_registry_citation_keys_missing == ("missing_registry_key",)
    assert audit.figure_registry_source_dois_missing == ("10.0000/missing-registry-doi",)
