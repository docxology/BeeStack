"""Behavioral regressions for manuscript custody, audit discovery and stale publication."""

from __future__ import annotations

import hashlib
import json
import runpy
from pathlib import Path

import pytest
from PIL import Image
from pypdf import PdfWriter

from beestack.figure_audit import audit_figures
from beestack.pipeline import bibliography_keys
from beestack.project_config import load_config
from beestack.publication_readiness import check_publication_readiness, manuscript_render_inputs
from beestack.source_audit import audit_sources, extract_pandoc_citation_keys

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _canonical(root: Path) -> Path:
    manuscript = root / "docs/manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "config.yaml").write_text("beestack:\n  seed: 42\n", encoding="utf-8")
    (manuscript / "references.bib").write_text(
        "@article{fixture, title={Fixture}}\n", encoding="utf-8"
    )
    return manuscript


def test_canonical_config_wins_over_obsolete_root_tree(tmp_path: Path) -> None:
    _canonical(tmp_path)
    obsolete = tmp_path / "manuscript"
    obsolete.mkdir()
    (obsolete / "config.yaml").write_text("beestack:\n  seed: 99\n", encoding="utf-8")
    assert load_config(tmp_path).seed == 42
    assert bibliography_keys(tmp_path) == ("fixture",)
    (tmp_path / "docs/manuscript/config.yaml").unlink()
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path)


@pytest.mark.parametrize("failure", ["missing", "empty", "unknown_token"])
def test_hydration_failure_preserves_every_prior_section(tmp_path: Path, failure: str) -> None:
    out = tmp_path / "output/manuscript"
    out.mkdir(parents=True)
    prior = {"00_abstract.md": "prior abstract", "obsolete.md": "prior appendix"}
    for name, text in prior.items():
        (out / name).write_text(text, encoding="utf-8")
    if failure != "missing":
        source = _canonical(tmp_path)
        if failure == "unknown_token":
            (source / "00_abstract.md").write_text("{{KNOWN}}", encoding="utf-8")
            (source / "01_intro.md").write_text("{{UNKNOWN}}", encoding="utf-8")
    hydrate = runpy.run_path(str(PROJECT_ROOT / "scripts/z_generate_manuscript_variables.py"))[
        "hydrate_manuscript"
    ]
    with pytest.raises((FileNotFoundError, ValueError, KeyError)):
        hydrate(tmp_path, {"KNOWN": "replacement"})
    assert {path.name: path.read_text(encoding="utf-8") for path in out.iterdir()} == prior


@pytest.mark.parametrize(
    ("attributes", "missing_label"), [("", True), ("{#fig:}", True), (" {#fig:known}", False)]
)
def test_image_discovery_does_not_require_a_valid_label(
    tmp_path: Path, attributes: str, missing_label: bool
) -> None:
    manuscript = tmp_path / "output/manuscript"
    manuscript.mkdir(parents=True)
    (manuscript / "01_intro.md").write_text(
        f"![Absent image](../figures/absent.png){attributes}\n", encoding="utf-8"
    )
    result = audit_figures(tmp_path, required_primary_artifacts=())
    assert result.image_reference_count == 1
    assert bool(result.missing_labels) is missing_label
    assert result.missing_image_paths == ("output/manuscript/01_intro.md:../figures/absent.png",)
    assert not result.passed


def test_narrative_citations_are_checked_without_treating_emails_as_sources(tmp_path: Path) -> None:
    text = "@missing argued; [-@present]. Email name@example.org and a+b@example.org. `@code` \\@escaped @fig:body @sec:intro"
    assert extract_pandoc_citation_keys(text) == ("missing", "present")
    source = _canonical(tmp_path)
    (source / "01_intro.md").write_text(text, encoding="utf-8")
    result = audit_sources(
        tmp_path,
        required_bib_dois={},
        registry_dois=(),
        figure_registry_citation_keys=(),
        figure_registry_source_dois=(),
    )
    assert result.missing_citation_keys == ("missing", "present")
    assert not result.passed


@pytest.mark.parametrize(
    "change",
    [
        "source",
        "new_source",
        "pdf",
        "readiness_report",
        "research_report",
        "raw_replace",
        "raw_delete",
        "raw_add",
        "malformed_receipt",
        "jpeg_replace",
        "jpeg_delete",
        "jpeg_sidecar_replace",
    ],
)
def test_publication_rejects_stale_source_or_pdf_bindings(tmp_path: Path, change: str) -> None:
    source = _canonical(tmp_path)
    (source / "00_abstract.md").write_text("# Abstract\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "2.0.0"\n', encoding="utf-8")
    (tmp_path / "uv.lock").write_text("version = 1\n", encoding="utf-8")
    (tmp_path / ".python-version").write_text("3.12.16\n", encoding="utf-8")
    pdf = tmp_path / "output/pdf/BeeStack_combined.pdf"
    pdf.parent.mkdir(parents=True)
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(pdf)
    reports = tmp_path / "output/reports"
    reports.mkdir()
    (reports / "project_readiness_review.json").write_text(
        '{"priority": "initial"}', encoding="utf-8"
    )
    (reports / "beestack_research_report.json").write_text('{"fraction": 0.5}', encoding="utf-8")
    raw = tmp_path / "output/data/empirical_sources/fixture/files/input.csv"
    raw.parent.mkdir(parents=True)
    raw.write_text("odor,bee,response\nA,g1,1\n", encoding="utf-8")
    image = tmp_path / "output/artifacts/support.jpg"
    image.parent.mkdir(parents=True)
    Image.new("RGB", (10, 10), "red").save(image)
    sidecar = image.with_suffix(".json")
    sidecar.write_text('{"caption": "Supporting illustration"}', encoding="utf-8")
    hydrated = tmp_path / "output/manuscript"
    hydrated.mkdir()
    (hydrated / "00_section.md").write_text(
        "![Supporting illustration](../artifacts/support.jpg) {#fig:support}\n", encoding="utf-8"
    )
    receipt = {
        "schema": "beestack.manuscript_render.v1",
        "pdf": "output/pdf/BeeStack_combined.pdf",
        "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "source_sha256": {
            path.relative_to(tmp_path).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in manuscript_render_inputs(tmp_path)
        },
    }
    (reports / "manuscript_render.json").write_text(json.dumps(receipt), encoding="utf-8")
    before = check_publication_readiness(tmp_path)
    assert before["checks"]["combined_pdf"] is True
    assert before["checks"]["manuscript_render_current"] is True
    if change == "source":
        (source / "00_abstract.md").write_text("# Changed evidence\n", encoding="utf-8")
    elif change == "new_source":
        (source / "01_intro.md").write_text("# New evidence\n", encoding="utf-8")
    elif change in {"readiness_report", "research_report"}:
        name = (
            "project_readiness_review.json"
            if change == "readiness_report"
            else "beestack_research_report.json"
        )
        (reports / name).write_text('{"changed": true}', encoding="utf-8")
    elif change == "raw_replace":
        raw.write_text("odor,bee,response\nA,g1,42\n", encoding="utf-8")
    elif change == "raw_delete":
        raw.unlink()
    elif change == "raw_add":
        raw.with_name("additional.csv").write_text("odor,bee,response\nB,g1,2\n", encoding="utf-8")
    elif change == "malformed_receipt":
        (reports / "manuscript_render.json").write_text("[]", encoding="utf-8")
    elif change == "jpeg_replace":
        Image.new("RGB", (10, 10), "blue").save(image)
    elif change == "jpeg_delete":
        image.unlink()
    elif change == "jpeg_sidecar_replace":
        sidecar.write_text('{"caption": "Different evidence"}', encoding="utf-8")
    else:
        with pdf.open("ab") as handle:
            handle.write(b"\n% changed bytes\n")
    after = check_publication_readiness(tmp_path)
    assert after["checks"]["manuscript_render_current"] is False
    assert after["ok"] is False


def test_publication_rejects_pdf_header_without_a_document(tmp_path: Path) -> None:
    _canonical(tmp_path)
    pdf = tmp_path / "output/pdf/BeeStack_combined.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"%PDF-1.4\n")
    result = check_publication_readiness(tmp_path)
    assert result["checks"]["combined_pdf"] is False


@pytest.mark.parametrize("change", ["prose", "report_value", "bibliography", "variable_file"])
def test_render_preflight_rejects_incompatible_hydration_without_overwriting_it(
    tmp_path: Path, change: str
) -> None:
    canonical = _canonical(tmp_path)
    for index in range(18):
        (canonical / f"{index:02d}_section.md").write_text(
            "# Section\n{{KNOWN}}\n", encoding="utf-8"
        )
    variables = {"KNOWN": "previous result"}
    hydrate = runpy.run_path(str(PROJECT_ROOT / "scripts/z_generate_manuscript_variables.py"))[
        "hydrate_manuscript"
    ]
    validate = runpy.run_path(str(PROJECT_ROOT / "scripts/render_manuscript.py"))[
        "validate_hydrated_manuscript"
    ]
    hydrate(tmp_path, variables)
    data = tmp_path / "output/data"
    data.mkdir()
    variable_path = data / "manuscript_variables.json"
    variable_path.write_text(json.dumps(variables), encoding="utf-8")
    checked = validate(tmp_path, variables)
    before = {path.name: path.read_bytes() for path in checked}
    if change == "prose":
        (canonical / "00_section.md").write_text(
            "# New ordinary prose\n{{KNOWN}}\n", encoding="utf-8"
        )
    elif change == "report_value":
        variables = {"KNOWN": "new result"}
    elif change == "bibliography":
        (canonical / "references.bib").write_text(
            "@article{new, title={New source}}\n", encoding="utf-8"
        )
    else:
        variable_path.write_text('{"KNOWN": "unrelated value"}', encoding="utf-8")
    with pytest.raises(ValueError):
        validate(tmp_path, variables)
    assert {path.name: path.read_bytes() for path in checked} == before


@pytest.mark.parametrize("extension", ["jpg", "svg"])
def test_every_referenced_image_requires_matching_provenance_outside_figures(tmp_path, extension):
    manuscript = tmp_path / "output/manuscript"
    manuscript.mkdir(parents=True)
    image = tmp_path / "output/artifacts" / f"support.{extension}"
    image.parent.mkdir()
    if extension == "jpg":
        Image.new("RGB", (10, 10), "red").save(image)
    else:
        image.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><circle cx="5" cy="5" r="4"/></svg>'
        )
    (manuscript / "00_section.md").write_text(
        f"![Supporting illustration](../artifacts/support.{extension}) {{#fig:support}}\n"
    )
    assert audit_figures(tmp_path, required_primary_artifacts=()).missing_sidecar_paths
    metadata = {
        "caption": "Supporting illustration",
        "alt_text": "Synthetic test graphic",
        "manuscript_section": "docs/manuscript/00_section.md",
        "manuscript_label": "fig:support",
        "claim_tier": "synthetic test fixture",
        "unsupported_inference": "Not empirical evidence",
        "artifact_kind": "figure",
        "source_data": ["synthetic fixture"],
        "regeneration_command": "test fixture",
    }
    sidecar = image.with_suffix(".json")
    sidecar.write_text(json.dumps(metadata))
    assert audit_figures(tmp_path, required_primary_artifacts=()).passed
    metadata["caption"] = "A conflicting scientific claim"
    sidecar.write_text(json.dumps(metadata))
    assert audit_figures(tmp_path, required_primary_artifacts=()).sidecar_manuscript_mismatches
    del metadata["unsupported_inference"]
    sidecar.write_text(json.dumps(metadata))
    assert audit_figures(tmp_path, required_primary_artifacts=()).sidecar_required_field_failures
