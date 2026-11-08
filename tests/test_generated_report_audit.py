from __future__ import annotations

import json
from pathlib import Path

import pytest

from beestack import audit_generated_reports


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
    (reports / "current.md").write_text("current evidence\n", encoding="utf-8")
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
                {
                    "artifact_path": "output/reports/current.md",
                    "availability_status": "generated",
                    "citation_keys": ("wilson2017good",),
                    "source_dois": ("not-a-doi",),
                    "artifact_kind": "report",
                    "claim_tier": "generated",
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
    assert not audit.project_root_path_leaks


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
                    "citation_keys": ("wilson2017good",),
                    "source_dois": ("10.1371/journal.pcbi.1005510",),
                    "artifact_kind": "report",
                    "claim_tier": "generated",
                },
                {
                    "artifact_path": "output/reports/empirical_analysis.md",
                    "availability_status": "network_gated_absent",
                    "citation_keys": ("paoli2024dryad",),
                    "source_dois": ("10.5061/dryad.qbzkh18sc",),
                    "artifact_kind": "report",
                    "claim_tier": "network_gated_absent",
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
    assert not audit.project_root_path_leaks


def test_generated_report_audit_flags_project_root_path_leakage(
    tmp_path: Path,
) -> None:
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
                    "citation_keys": ("wilson2017good",),
                    "source_dois": ("10.1371/journal.pcbi.1005510",),
                    "artifact_kind": "report",
                    "claim_tier": "generated",
                }
            ]
        },
    )
    (reports / "methods_analysis.md").write_text("current evidence\n", encoding="utf-8")
    _write_json(reports / "beestack_research_report.json", {"empirical_evidence": []})
    (reports / "beestack_research_report.md").write_text(
        "- Empirical registry/evidence rows: `0`\n",
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
    leaked_path = tmp_path.resolve() / "output" / "figures" / "empirical" / "leak.png"
    _write_json(data / "empirical_analysis.json", {"figure_paths": [str(leaked_path)]})

    audit = audit_generated_reports(tmp_path)

    assert not audit.passed
    assert audit.project_root_path_leaks == ("output/data/empirical_analysis.json",)


def test_analysis_unavailable_cannot_support_current_claims(tmp_path: Path) -> None:
    reports = tmp_path / "output" / "reports"
    reports.mkdir(parents=True)
    (reports / "methods_analysis.md").write_text(
        "- analysis_unavailable supports a current empirical conclusion\n", encoding="utf-8"
    )
    audit = audit_generated_reports(tmp_path)
    assert not audit.passed
    assert audit.stale_report_paths == ()
    assert audit.missing_current_evidence_paths == ()
    assert audit.project_root_path_leaks == ()


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("citation_keys", []),
        ("source_dois", []),
        ("source_dois", ["not-a-doi"]),
        ("artifact_kind", ""),
        ("claim_tier", ""),
    ),
)
def test_current_claim_metadata_must_be_complete_and_citable(
    tmp_path: Path, field: str, value: object
) -> None:
    artifact = tmp_path / "output" / "reports" / "current.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("Current generated report\n", encoding="utf-8")
    metadata = {
        "artifact_path": "output/reports/current.md",
        "availability_status": "generated",
        "citation_keys": ["wilson2017good"],
        "source_dois": ["10.1371/journal.pcbi.1005510"],
        "artifact_kind": "report",
        "claim_tier": "generated",
    }
    path = tmp_path / "output" / "data" / "methods_analysis.json"
    _write_json(path, {"manuscript_evidence_links": [metadata]})
    assert audit_generated_reports(tmp_path).passed
    metadata[field] = value
    _write_json(path, {"manuscript_evidence_links": [metadata]})
    assert not audit_generated_reports(tmp_path).passed


@pytest.mark.parametrize(("records", "passed"), ((0, False), (1, True)))
def test_current_empirical_claim_requires_observed_records(
    tmp_path: Path, records: int, passed: bool
) -> None:
    _write_json(
        tmp_path / "output" / "reports" / "beestack_research_report.json",
        {
            "empirical_evidence": [
                {"dataset_id": "calcium", "availability_status": "parsed", "local_records": records}
            ]
        },
    )
    assert audit_generated_reports(tmp_path).passed is passed
