from __future__ import annotations

import json
from pathlib import Path

from beestack import audit_generated_reports, generated_report_audit_markdown


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_generated_report_audit_flags_stale_tests_and_unsupported_claims(
    tmp_path: Path,
) -> None:
    reports = tmp_path / "output" / "reports"
    data = tmp_path / "output" / "data"
    reports.mkdir(parents=True)
    (reports / "test_results.md").write_text("stale local result\n", encoding="utf-8")
    (reports / "methods_analysis.md").write_text(
        "- `section` BeeBrain: `output/reports/empirical_analysis.md` "
        "(empirical_analysis, network_gated_absent) supports absent evidence\n",
        encoding="utf-8",
    )
    _write_json(
        data / "methods_analysis.json",
        {
            "manuscript_evidence_links": [
                {
                    "artifact_path": "output/reports/missing_current.md",
                    "availability_status": "generated",
                },
                {
                    "artifact_path": "output/reports/empirical_analysis.md",
                    "availability_status": "network_gated_absent",
                },
            ]
        },
    )
    _write_json(
        reports / "beestack_research_report.json",
        {
            "empirical_evidence": [
                {
                    "dataset_id": "calcium",
                    "availability_status": "parsed",
                    "local_records": 0,
                }
            ]
        },
    )
    (reports / "beestack_research_report.md").write_text(
        "- Empirical evidence records: `1`\n",
        encoding="utf-8",
    )
    _write_json(
        reports / "stack_synthesis_review.json",
        {
            "validations": [
                {
                    "name": "empirical_parseability",
                    "passed": False,
                    "detail": "BeeBrain parseable-source fraction clears configured minimum.",
                }
            ]
        },
    )

    audit = audit_generated_reports(tmp_path)

    assert not audit.passed
    assert audit.stale_report_paths == ("output/reports/test_results.md",)
    assert audit.missing_current_evidence_paths == ("output/reports/missing_current.md",)
    assert any("supports absent evidence" in claim for claim in audit.unsupported_report_claims)
    assert any(
        "marked parsed with zero local records" in claim
        for claim in audit.unsupported_report_claims
    )
    assert "Generated Report Audit" in generated_report_audit_markdown(audit)


def test_generated_report_audit_allows_gated_absent_evidence(tmp_path: Path) -> None:
    reports = tmp_path / "output" / "reports"
    data = tmp_path / "output" / "data"
    current = reports / "current.md"
    current.parent.mkdir(parents=True)
    current.write_text("current evidence\n", encoding="utf-8")
    _write_json(
        data / "methods_analysis.json",
        {
            "manuscript_evidence_links": [
                {
                    "artifact_path": "output/reports/current.md",
                    "availability_status": "generated",
                },
                {
                    "artifact_path": "output/reports/empirical_analysis.md",
                    "availability_status": "network_gated_absent",
                },
            ]
        },
    )
    (reports / "methods_analysis.md").write_text(
        "- gated evidence is network_gated_absent and is gated for current claims\n",
        encoding="utf-8",
    )
    _write_json(
        reports / "beestack_research_report.json",
        {
            "empirical_evidence": [
                {
                    "dataset_id": "calcium",
                    "availability_status": "network_gated_absent",
                    "local_records": 0,
                }
            ]
        },
    )
    (reports / "beestack_research_report.md").write_text(
        "- Empirical registry/evidence rows: `1`\n",
        encoding="utf-8",
    )
    _write_json(
        reports / "stack_synthesis_review.json",
        {
            "validations": [
                {
                    "name": "empirical_parseability",
                    "passed": False,
                    "detail": "BeeBrain parseable-source fraction does not clear configured minimum.",
                }
            ]
        },
    )

    audit = audit_generated_reports(tmp_path)

    assert audit.passed
