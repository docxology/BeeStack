"""Generated-report freshness and claim-consistency audit helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CURRENT_EVIDENCE_STATES = frozenset({"parsed", "generated"})
ABSENT_EVIDENCE_STATES = frozenset(
    {"registered_absent", "network_gated_absent", "missing_optional"}
)
STALE_REPORT_NAMES = ("test_results.json", "test_results.md")


@dataclass(frozen=True)
class GeneratedReportAudit:
    """Freshness and semantic-consistency audit for generated reports."""

    stale_report_paths: tuple[str, ...]
    missing_current_evidence_paths: tuple[str, ...]
    unsupported_report_claims: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not (
            self.stale_report_paths
            or self.missing_current_evidence_paths
            or self.unsupported_report_claims
        )

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["passed"] = self.passed
        return payload


def audit_generated_reports(project_root: Path) -> GeneratedReportAudit:
    """Audit generated reports for stale files and unsupported evidence claims."""

    reports_dir = project_root / "output" / "reports"
    data_dir = project_root / "output" / "data"
    stale_reports = tuple(
        _relative(project_root, reports_dir / name)
        for name in STALE_REPORT_NAMES
        if (reports_dir / name).exists()
    )
    methods = _read_json(data_dir / "methods_analysis.json")
    synthesis = _read_json(reports_dir / "stack_synthesis_review.json")
    research = _read_json(reports_dir / "beestack_research_report.json")
    missing_evidence = _missing_current_evidence_paths(project_root, methods)
    unsupported = tuple(
        dict.fromkeys(
            (
                *_unsupported_method_markdown_claims(reports_dir / "methods_analysis.md"),
                *_unsupported_research_claims(
                    reports_dir / "beestack_research_report.md", research
                ),
                *_unsupported_synthesis_claims(synthesis),
            )
        )
    )
    return GeneratedReportAudit(stale_reports, missing_evidence, unsupported)


def generated_report_audit_markdown(audit: GeneratedReportAudit) -> str:
    """Render generated-report audit results as Markdown."""

    lines = [
        "# BeeStack Generated Report Audit",
        "",
        f"- Passed: `{audit.passed}`",
        f"- Stale report files: `{len(audit.stale_report_paths)}`",
        f"- Missing current evidence paths: `{len(audit.missing_current_evidence_paths)}`",
        f"- Unsupported report claims: `{len(audit.unsupported_report_claims)}`",
        "",
        "## Stale Report Files",
        "",
    ]
    lines.extend(_list_or_none(audit.stale_report_paths))
    lines.extend(["", "## Missing Current Evidence Paths", ""])
    lines.extend(_list_or_none(audit.missing_current_evidence_paths))
    lines.extend(["", "## Unsupported Report Claims", ""])
    lines.extend(_list_or_none(audit.unsupported_report_claims))
    lines.append("")
    return "\n".join(lines)


def _missing_current_evidence_paths(
    project_root: Path, methods_analysis: dict[str, Any]
) -> tuple[str, ...]:
    missing: list[str] = []
    for link in methods_analysis.get("manuscript_evidence_links", ()) or ():
        status = str(link.get("availability_status", "generated"))
        artifact_path = str(link.get("artifact_path", ""))
        if not artifact_path or status not in CURRENT_EVIDENCE_STATES:
            continue
        path = Path(artifact_path)
        if not path.is_absolute():
            path = project_root / artifact_path
        if not path.exists():
            missing.append(artifact_path)
    return tuple(sorted(dict.fromkeys(missing)))


def _unsupported_method_markdown_claims(path: Path) -> tuple[str, ...]:
    if not path.exists():
        return ()
    claims: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        lowered = line.lower()
        if any(status in lowered for status in ABSENT_EVIDENCE_STATES) and " supports " in lowered:
            claims.append(f"Absent evidence rendered as support: {line.strip()}")
    return tuple(claims)


def _unsupported_research_claims(path: Path, research_report: dict[str, Any]) -> tuple[str, ...]:
    claims: list[str] = []
    if path.exists() and "Empirical evidence records" in path.read_text(
        encoding="utf-8", errors="replace"
    ):
        claims.append("Research report uses ambiguous 'Empirical evidence records' wording.")
    for record in research_report.get("empirical_evidence", ()) or ():
        status = str(record.get("availability_status", ""))
        local_records = int(record.get("local_records", 0) or 0)
        dataset_id = str(record.get("dataset_id", "unknown empirical dataset"))
        if not status:
            claims.append(f"{dataset_id} is missing an availability_status field.")
        elif status == "parsed" and local_records == 0:
            claims.append(f"{dataset_id} is marked parsed with zero local records.")
    return tuple(claims)


def _unsupported_synthesis_claims(synthesis_review: dict[str, Any]) -> tuple[str, ...]:
    claims: list[str] = []
    for validation in synthesis_review.get("validations", ()) or ():
        if bool(validation.get("passed", False)):
            continue
        detail = str(validation.get("detail", ""))
        lowered = detail.lower()
        if " clears " in f" {lowered} " or " meets " in f" {lowered} ":
            claims.append(
                f"{validation.get('name', 'unnamed')} failed but uses success wording: {detail}"
            )
    return tuple(claims)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _list_or_none(values: tuple[str, ...]) -> list[str]:
    return [f"- `{value}`" for value in values] if values else ["- None detected."]


def _relative(project_root: Path, path: Path) -> str:
    return path.resolve().relative_to(project_root.resolve()).as_posix()
