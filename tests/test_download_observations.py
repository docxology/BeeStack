"""Current filesystem evidence must supersede historical download counters.

All payloads and completion records here are isolated synthetic parser fixtures,
not acquired empirical data or biological-validation evidence.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from beestack.brain.datasets import empirical_anatomy_datasets
from beestack.brain.empirical_parsers.anatomy_loader import load_anatomy
from beestack.brain.empirical_status import archive_status, catalog_status
from beestack.security import completed_download, completion_path
from beestack.security.path_safety import download_source_identity

FIXTURE_URL = "https://ndownloader.figshare.com/files/101"
FIXTURE_DOI = "10.6084/m9.figshare.101.v1"


def _sealed_file(path: Path, content: bytes = b"fixture,value\n1,2\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    completion_path(path).write_text(
        json.dumps(
            {
                "size": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
                "source_identity": download_source_identity(
                    FIXTURE_URL, doi=FIXTURE_DOI, size=len(content)
                ),
            }
        ),
        encoding="utf-8",
    )
    return path


def _catalog_row(path: Path) -> dict:
    return {
        "dataset_id": "fixture",
        "local_file": str(path),
        "file_downloaded": True,
        "download_url": FIXTURE_URL,
        "doi": FIXTURE_DOI,
        "size": len(b"fixture,value\n1,2\n"),
    }


def test_missing_atlas_payloads_cannot_inherit_historical_download_success(tmp_path) -> None:
    source = tmp_path / "sources"
    source.mkdir()
    dataset = empirical_anatomy_datasets()[0]
    asset = dataset.assets[0]
    foreign = _sealed_file(tmp_path / "unrelated" / asset.file_name)
    manifest = source / "anatomy_downloads.json"
    manifest.write_text(
        json.dumps(
            [
                {
                    "dataset_id": dataset.dataset_id,
                    "asset_id": asset.asset_id,
                    "url": asset.url,
                    "local_path": str(foreign),
                    "size_bytes": foreign.stat().st_size,
                    "downloaded": True,
                    "skipped_existing": False,
                }
            ]
        ),
        encoding="utf-8",
    )
    original = manifest.read_bytes()
    summary, _, _, records = load_anatomy(source)
    assert summary.downloaded_asset_count == 0
    assert not any(record.downloaded for record in records)
    assert all(Path(record.local_path).is_relative_to(source) for record in records)
    assert manifest.read_bytes() == original


def test_catalog_completion_is_current_source_bound_and_cwd_independent(
    tmp_path, monkeypatch
) -> None:
    source = tmp_path / "output/data/empirical_sources"
    local = _sealed_file(source / "fixture/files/data.csv")
    foreign = _sealed_file(tmp_path / "unrelated/data.csv")
    rows = [
        _catalog_row(local.relative_to(tmp_path)),
        _catalog_row(foreign),
        _catalog_row(source / "fixture/missing.csv"),
    ]
    (source / "catalog.json").write_text(json.dumps(rows), encoding="utf-8")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    assert [row["file_downloaded"] for row in catalog_status(source, project_root=tmp_path)] == [
        True,
        False,
        False,
    ]
    local.write_bytes(b"changed after the recorded transfer")
    assert not any(row["file_downloaded"] for row in catalog_status(source, project_root=tmp_path))


def test_archive_counts_only_distinct_current_verified_files(tmp_path) -> None:
    source = tmp_path / "sources"
    local = _sealed_file(source / "fixture/files/data.csv")
    archive = _sealed_file(source / "fixture/archive.zip")
    foreign = _sealed_file(tmp_path / "unrelated/data.csv")
    (source / "catalog.json").write_text(json.dumps([_catalog_row(local)]), encoding="utf-8")
    (source / "archives.json").write_text(
        json.dumps(
            [
                {
                    "dataset_id": "fixture",
                    "archive_downloaded": True,
                    "local_archive": str(archive),
                    "doi": FIXTURE_DOI,
                    "archive_download_url": FIXTURE_URL,
                    "archive_expected_size_bytes": len(b"fixture,value\n1,2\n"),
                    "file_downloaded_count": 99,
                    "downloaded_file_paths": [
                        str(local),
                        str(local.relative_to(tmp_path)),
                        str(foreign),
                        str(source / "fixture/missing.csv"),
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )
    row = archive_status(source, project_root=tmp_path)[0]
    assert row["archive_downloaded"]
    assert row["file_downloaded_count"] == 1
    archive.unlink()
    row = archive_status(source, project_root=tmp_path)[0]
    assert not row["archive_downloaded"]
    assert row["file_downloaded_count"] == 1


@pytest.mark.parametrize("filename", ["catalog.json", "archives.json"])
@pytest.mark.parametrize("payload", [{"downloaded": True}, [True]])
def test_malformed_manifests_are_not_empty_successful_observations(
    tmp_path, filename, payload
) -> None:
    (tmp_path / filename).write_text(json.dumps(payload), encoding="utf-8")
    reader = catalog_status if filename == "catalog.json" else archive_status
    with pytest.raises(ValueError):
        reader(tmp_path)


def test_completion_receipts_do_not_certify_symbolic_payload_or_marker(tmp_path) -> None:
    actual = _sealed_file(tmp_path / "actual/data.csv")
    alias = tmp_path / "alias.csv"
    alias.symlink_to(actual)
    completion_path(alias).write_bytes(completion_path(actual).read_bytes())
    assert not completed_download(alias)
    marker = completion_path(actual)
    saved = tmp_path / "saved-marker.json"
    marker.rename(saved)
    marker.symlink_to(saved)
    assert not completed_download(actual)
