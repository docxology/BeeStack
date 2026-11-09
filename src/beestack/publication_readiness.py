"""Publication readiness gate for the current BeeStack manuscript release."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any

import yaml
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from beestack.brain.empirical_status import current_empirical_analysis, empirical_input_paths
from beestack.config import config_from_mapping
from beestack.figure_audit import manuscript_image_references
from beestack.generated_report_audit import audit_generated_reports
from beestack.manuscript_variables import MANUSCRIPT_ARTIFACT_PATHS
from beestack.security.posture import audit_security_posture
from beestack.utils import sha256_file
from beestack.version import MANUSCRIPT_VERSION, PACKAGE_VERSION

_COMBINED_PDF = "BeeStack_combined.pdf"
_LEGACY_PDF = "beestack_manuscript.pdf"
_DOI_SHAPE_RE = re.compile(r"^10\.[0-9]{4,9}/[^\s\x00-\x1f\x7f]+$")
# Primary deposit metadata: https://zenodo.org/api/records/20420557, version 1.0.
_HISTORICAL_VERSION_1_DOI = "10.5281/zenodo.20420557"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_manuscript_config(project_root: Path) -> dict[str, Any]:
    config_path = project_root / "docs" / "manuscript" / "config.yaml"
    if not config_path.is_file():
        return {}
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def _pyproject_version(project_root: Path) -> str:
    pyproject = project_root / "pyproject.toml"
    if not pyproject.is_file():
        return ""
    return str(
        tomllib.loads(pyproject.read_text(encoding="utf-8")).get("project", {}).get("version", "")
    )


def manuscript_render_inputs(project_root: Path) -> tuple[Path, ...]:
    """Exact source/data/figure inputs sealed by the local manuscript renderer."""

    inputs = [project_root / name for name in ("pyproject.toml", "uv.lock", ".python-version")]
    inputs.extend(empirical_input_paths(project_root))
    for reference in manuscript_image_references(project_root):
        # Use the same resolved dependencies as figure preflight, regardless of
        # image format or project-local directory. Outside-root paths refuse
        # when receipt keys are constructed, rather than escaping the seal.
        inputs.append(reference.resolved_path)
        sidecar = reference.resolved_path.with_suffix(".json")
        if sidecar.is_file():
            inputs.append(sidecar)
    for directory, pattern in (
        ("docs/manuscript", "*.md"),
        ("docs/manuscript", "*.yaml"),
        ("docs/manuscript", "*.bib"),
        ("output/manuscript", "*.md"),
        ("output/manuscript", "*.yaml"),
        ("output/manuscript", "*.bib"),
        ("src", "*.py"),
        ("scripts", "*.py"),
        ("scripts", "*.lua"),
        ("output/data", "*.json"),
        ("output/figures", "*.png"),
        ("output/figures", "*.json"),
    ):
        inputs.extend((project_root / directory).rglob(pattern))
    inputs.extend(
        project_root / relative
        for relative in MANUSCRIPT_ARTIFACT_PATHS.values()
        if (project_root / relative).is_file()
    )
    return tuple(sorted(set(inputs)))


def _render_is_current(root: Path, pdf: Path) -> bool:
    try:
        receipt = _read_json(root / "output/reports/manuscript_render.json")
        if not isinstance(receipt, dict):
            return False
        expected = {
            path.relative_to(root).as_posix(): path for path in manuscript_render_inputs(root)
        }
        hashes = receipt.get("source_sha256")
        if not isinstance(hashes, dict) or hashes.keys() != expected.keys() or not pdf.is_file():
            return False
        return (
            receipt.get("schema") == "beestack.manuscript_render.v1"
            and receipt.get("pdf") == "output/pdf/BeeStack_combined.pdf"
            and receipt.get("pdf_sha256") == sha256_file(pdf)
            and all(
                path.is_file() and hashes[name] == sha256_file(path)
                for name, path in expected.items()
            )
        )
    except (OSError, ValueError, RuntimeError):
        return False


def check_publication_readiness(
    project_root: Path,
    *,
    require_doi: bool = False,
) -> dict[str, object]:
    """Return structured checks; a real, source-bound combined PDF is mandatory."""

    root = project_root.resolve()
    checks: dict[str, bool] = {}
    blockers: list[str] = []
    warnings: list[str] = []

    config = _read_manuscript_config(root)
    paper_version = str((config.get("paper") or {}).get("version", "")).strip()
    checks["manuscript_version"] = paper_version == MANUSCRIPT_VERSION
    if not checks["manuscript_version"]:
        blockers.append(
            f"docs/manuscript/config.yaml paper.version must be {MANUSCRIPT_VERSION!r} "
            f"(found {paper_version!r})"
        )

    pyproject_version = _pyproject_version(root)
    checks["package_version"] = pyproject_version == PACKAGE_VERSION
    if not checks["package_version"]:
        blockers.append(
            f"pyproject.toml version must be {PACKAGE_VERSION!r} (found {pyproject_version!r})"
        )

    doi = str((config.get("publication") or {}).get("doi", "")).strip()
    checks["doi_configured"] = bool(doi)
    checks["doi_shape_and_history_valid"] = bool(
        _DOI_SHAPE_RE.fullmatch(doi) and doi.casefold() != _HISTORICAL_VERSION_1_DOI
    )
    if not checks["doi_configured"]:
        message = "publication.doi not set in docs/manuscript/config.yaml"
        if require_doi:
            blockers.append(message)
        else:
            warnings.append(f"{message} (mint Zenodo DOI before public deposit)")
    elif not checks["doi_shape_and_history_valid"]:
        message = (
            "publication.doi identifies historical release 1.0, not the current version"
            if doi.casefold() == _HISTORICAL_VERSION_1_DOI
            else "publication.doi must be a bare DOI with a valid registrant/suffix shape"
        )
        (blockers if require_doi else warnings).append(message)

    combined_pdf = root / "output" / "pdf" / _COMBINED_PDF
    try:
        checks["combined_pdf"] = combined_pdf.is_file() and bool(
            PdfReader(combined_pdf, strict=True).pages
        )
    except (OSError, PdfReadError, ValueError):
        checks["combined_pdf"] = False
    if not checks["combined_pdf"]:
        blockers.append(f"missing or unreadable output/pdf/{_COMBINED_PDF}")
    checks["manuscript_render_current"] = _render_is_current(root, combined_pdf)
    if not checks["manuscript_render_current"]:
        blockers.append(
            "combined PDF lacks a current source/data/figure-bound manuscript render receipt"
        )

    legacy_pdf = root / "output" / "pdf" / _LEGACY_PDF
    if legacy_pdf.is_file():
        checks["legacy_pdf_absent"] = False
        warnings.append(
            f"stale output/pdf/{_LEGACY_PDF} present; use {_COMBINED_PDF} only "
            "(remove legacy artifact or regenerate)"
        )
    else:
        checks["legacy_pdf_absent"] = True

    variables_path = root / "output" / "data" / "manuscript_variables.json"
    if variables_path.is_file():
        text = variables_path.read_text(encoding="utf-8")
        checks["manuscript_variables_hydrated"] = "{{" not in text
        if not checks["manuscript_variables_hydrated"]:
            blockers.append("unresolved {{TOKENS}} in manuscript_variables.json")
    else:
        checks["manuscript_variables_hydrated"] = False
        blockers.append("missing output/data/manuscript_variables.json")
    sources = tuple((root / "docs/manuscript").glob("[0-9][0-9]_*.md"))
    checks["manuscript_sections_hydrated"] = len(sources) == 18 and all(
        (rendered := root / "output/manuscript" / source.name).is_file()
        and "{{" not in rendered.read_text(encoding="utf-8")
        for source in sources
    )
    if not checks["manuscript_sections_hydrated"]:
        blockers.append("missing or unresolved hydrated manuscript sections")

    security = audit_security_posture(root)
    checks["security_posture"] = security.passed
    if not security.passed:
        blockers.append("security posture audit failed")

    generated = audit_generated_reports(root)
    checks["generated_report_audit"] = generated.passed
    if not generated.passed:
        blockers.append("generated report audit failed")

    empirical = current_empirical_analysis(root, config_from_mapping(config.get("beestack", {})))
    checks["empirical_analysis_current"] = empirical.get("availability_status") == "current"
    if not checks["empirical_analysis_current"]:
        warnings.append(
            "No current odor-response panel analysis; retained empirical figures/reports are historical and manuscript values are unavailable, not zero."
        )
    completeness = empirical.get("brain_data_completeness", {})
    parseable_fraction = completeness.get("parseable_fraction")
    parseability_target = completeness.get("parseability_target")
    parseability_satisfied = bool(completeness.get("parseability_target_satisfied"))
    checks["parseability_target_satisfied"] = parseability_satisfied
    if (
        isinstance(parseable_fraction, (int, float))
        and isinstance(parseability_target, (int, float))
        and float(parseable_fraction) < float(parseability_target)
        and parseability_satisfied
    ):
        checks["parseability_flag_consistent"] = False
        blockers.append(
            "brain_data_completeness.json marks parseability_target_satisfied=true "
            f"but parseable_fraction={parseable_fraction} < target={parseability_target}"
        )
    else:
        checks["parseability_flag_consistent"] = True
    if (
        isinstance(parseable_fraction, (int, float))
        and isinstance(parseability_target, (int, float))
        and float(parseable_fraction) < float(parseability_target)
    ):
        warnings.append(
            "brain parseability target not met "
            f"(parseable_fraction={parseable_fraction}); "
            "documented in limitations and roadmap — not a release blocker"
        )

    # Headline-honesty binding (iter-11): a perfect config-band self-test rate may
    # not be published without acknowledged limitations. overall_validation_fraction
    # is a mean of module threshold checks, structurally disjoint from known_gaps;
    # this gate prevents the run from claiming full validation while cataloguing zero
    # gaps (the over-claim state the prior oracle was blind to).
    research = _read_json(root / "output" / "data" / "research_suite_report.json")
    overall_validation = research.get("overall_validation_fraction")
    known_gaps = research.get("known_gaps")
    if isinstance(overall_validation, (int, float)) and float(overall_validation) >= 1.0:
        gaps_disclosed = isinstance(known_gaps, list) and len(known_gaps) > 0
        checks["validation_fraction_discloses_gaps"] = gaps_disclosed
        if not gaps_disclosed:
            blockers.append(
                "research_suite_report.json reports overall_validation_fraction>=1.0 "
                "with zero known_gaps: a perfect config-band self-test rate published "
                "without any acknowledged limitation is an over-claim"
            )
    else:
        checks["validation_fraction_discloses_gaps"] = True

    changelog = root / "CHANGELOG.md"
    checks["changelog_present"] = changelog.is_file()
    if not checks["changelog_present"]:
        blockers.append("missing CHANGELOG.md for the current release")

    ok = not blockers
    return {
        "ok": ok,
        "release": MANUSCRIPT_VERSION,
        "package_version": PACKAGE_VERSION,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
    }
