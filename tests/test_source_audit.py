from __future__ import annotations

from pathlib import Path

from beestack.source_audit import (
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
