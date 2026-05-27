"""Publication readiness gate for BeeStack 1.0 manuscript release."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from beestack.generated_report_audit import audit_generated_reports
from beestack.security.posture import audit_security_posture
from beestack.version import MANUSCRIPT_VERSION, PACKAGE_VERSION

_COMBINED_PDF = "BeeStack_combined.pdf"
_LEGACY_PDF = "beestack_manuscript.pdf"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_manuscript_config(project_root: Path) -> dict[str, Any]:
    config_path = project_root / "manuscript" / "config.yaml"
    if not config_path.is_file():
        return {}
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def _pyproject_version(project_root: Path) -> str:
    pyproject = project_root / "pyproject.toml"
    if not pyproject.is_file():
        return ""
    match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject.read_text(encoding="utf-8"), re.M)
    return match.group(1) if match else ""


def check_publication_readiness(
    project_root: Path,
    *,
    require_doi: bool = False,
) -> dict[str, object]:
    """Return structured gate results for a BeeStack 1.0 release."""

    root = project_root.resolve()
    checks: dict[str, bool] = {}
    blockers: list[str] = []
    warnings: list[str] = []

    config = _read_manuscript_config(root)
    paper_version = str((config.get("paper") or {}).get("version", "")).strip()
    checks["manuscript_version_1_0"] = paper_version == MANUSCRIPT_VERSION
    if not checks["manuscript_version_1_0"]:
        blockers.append(
            f"manuscript/config.yaml paper.version must be {MANUSCRIPT_VERSION!r} "
            f"(found {paper_version!r})"
        )

    pyproject_version = _pyproject_version(root)
    checks["package_version_1_0_0"] = pyproject_version == PACKAGE_VERSION
    if not checks["package_version_1_0_0"]:
        blockers.append(
            f"pyproject.toml version must be {PACKAGE_VERSION!r} (found {pyproject_version!r})"
        )

    doi = str((config.get("publication") or {}).get("doi", "")).strip()
    checks["doi_configured"] = bool(doi)
    if not checks["doi_configured"]:
        message = "publication.doi not set in manuscript/config.yaml"
        if require_doi:
            blockers.append(message)
        else:
            warnings.append(f"{message} (mint Zenodo DOI before public deposit)")

    combined_pdf = root / "output" / "pdf" / _COMBINED_PDF
    checks["combined_pdf"] = combined_pdf.is_file()
    if not checks["combined_pdf"]:
        blockers.append(f"missing output/pdf/{_COMBINED_PDF}")

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

    security = audit_security_posture(root)
    checks["security_posture"] = security.passed
    if not security.passed:
        blockers.append("security posture audit failed")

    generated = audit_generated_reports(root)
    checks["generated_report_audit"] = generated.passed
    if not generated.passed:
        blockers.append("generated report audit failed")

    completeness = _read_json(root / "output" / "data" / "brain_data_completeness.json")
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

    changelog = root / "CHANGELOG.md"
    checks["changelog_present"] = changelog.is_file()
    if not checks["changelog_present"]:
        blockers.append("missing CHANGELOG.md for release 1.0")

    ok = not blockers
    return {
        "ok": ok,
        "release": MANUSCRIPT_VERSION,
        "package_version": PACKAGE_VERSION,
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
    }
