from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path

import pytest

from beestack.security import (
    SecurityPostureAudit,
    assert_safe_zip_member,
    audit_security_posture,
    resolve_under_root,
    safe_relative_path,
    security_posture_markdown,
    validate_download_url,
    validate_zip_archive_bounds,
)


def test_validate_download_url_accepts_curated_hosts() -> None:
    validate_download_url("https://datadryad.org/api/v2/files/1/download")
    validate_download_url(
        "https://dryad-assetstore-merritt-west.s3.us-west-2.amazonaws.com/v3/307381/data/file.zip"
    )
    validate_download_url("https://mdpi-res.com/d_attachment/insects/insects-14-00539/article_deploy/insects-14-00539-s001.zip")
    validate_download_url(
        "https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/44977549/features.csv"
    )
    validate_download_url(
        "https://www.bcp.fu-berlin.de/biologie/arbeitsgruppen/neurobiologie/ag_menzel/beebrain/download/_hsb/HBSGrey.zip"
    )


def test_validate_download_url_rejects_unlisted_host() -> None:
    with pytest.raises(ValueError, match="allowlist"):
        validate_download_url("https://example.com/payload.zip")


def test_validate_download_url_rejects_non_https() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        validate_download_url("http://datadryad.org/api/v2/files/1/download")


def test_validate_download_url_rejects_missing_host_and_accepts_dryad_lambda() -> None:
    with pytest.raises(ValueError, match="missing host"):
        validate_download_url("https:///payload.zip", context="unit")
    validate_download_url("https://example.lambda-url.us-west-2.on.aws/payload.zip")


def test_safe_relative_path_strips_traversal() -> None:
    assert safe_relative_path("../etc/passwd").as_posix() == "etc/passwd"
    assert safe_relative_path("nested/file.csv").as_posix() == "nested/file.csv"
    assert safe_relative_path("../../").as_posix() == "payload"


def test_assert_safe_zip_member_rejects_traversal() -> None:
    with pytest.raises(ValueError, match="traversal"):
        assert_safe_zip_member("../../escape.txt")
    with pytest.raises(ValueError, match="absolute"):
        assert_safe_zip_member("/absolute/escape.txt")


def test_zip_slip_member_is_rejected_during_ingest_scan() -> None:
    payload = BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("../evil.csv", "Bee,Plume,Frame,Odor_detector,LeftTheta,RightTheta\n")
    payload.seek(0)
    with zipfile.ZipFile(payload) as archive:
        for info in archive.infolist():
            with pytest.raises(ValueError, match="traversal"):
                assert_safe_zip_member(info.filename)


def test_validate_zip_archive_bounds_rejects_oversized_member_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("beestack.security.path_safety.MAX_ZIP_MEMBER_COUNT", 2)
    payload = BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        for index in range(3):
            archive.writestr(f"file_{index}.txt", "x")
    payload.seek(0)
    with zipfile.ZipFile(payload) as archive, pytest.raises(ValueError, match="member cap"):
        validate_zip_archive_bounds(archive)


def test_validate_zip_archive_bounds_rejects_uncompressed_size(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("beestack.security.path_safety.MAX_ZIP_UNCOMPRESSED_BYTES", 2)
    payload = BytesIO()
    with zipfile.ZipFile(payload, "w") as archive:
        archive.writestr("file.txt", "bee")
    payload.seek(0)
    with zipfile.ZipFile(payload) as archive, pytest.raises(
        ValueError, match="uncompressed size cap"
    ):
        validate_zip_archive_bounds(archive)


def test_resolve_under_root_blocks_traversal(tmp_path: Path) -> None:
    assert resolve_under_root(tmp_path, Path("nested/file.txt")) == (
        tmp_path / "nested" / "file.txt"
    )
    with pytest.raises(ValueError, match="escapes"):
        resolve_under_root(tmp_path, Path("../outside.txt"))


def test_validate_download_url_rejects_redirect_target_host() -> None:
    """Post-redirect validation must reject hosts outside the allowlist."""
    with pytest.raises(ValueError, match="allowlist"):
        validate_download_url(
            "https://example.com/evil.zip",
            context="download_url redirect",
        )


def test_security_posture_audit_passes_on_project_root() -> None:
    project_root = Path(__file__).resolve().parents[1]
    audit = audit_security_posture(project_root)
    assert audit.threat_model_present
    assert audit.security_doc_present
    assert audit.uv_lock_present
    assert not audit.registry_url_violations
    assert audit.passed


def test_security_posture_markdown_reports_failures() -> None:
    audit = SecurityPostureAudit(
        threat_model_present=False,
        security_doc_present=False,
        uv_lock_present=False,
        registry_url_violations=("https://example.org/payload.zip",),
        forbidden_pattern_hits=("src/example.py:eval(",),
        urllib_modules=(),
        passed=False,
    )
    markdown = security_posture_markdown(audit)

    assert "Status: **failed**" in markdown
    assert "Registry URL violations" in markdown
    assert "Forbidden pattern hits" in markdown
    assert "src/example.py:eval(" in markdown
