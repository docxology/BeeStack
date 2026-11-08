"""Refused locators must not disclose credentials through errors or catalogs."""

from __future__ import annotations

import json

import pytest

from beestack.brain import empirical_fetch
from beestack.security import validate_download_url

CASES = [
    ("https://fixture-user:fixture-password@datadryad.org/file", "fixture-password"),
    ("http://datadryad.org/file?token=fixture-query-secret", "fixture-query-secret"),
    ("https://example.org/file?token=fixture-query-secret", "fixture-query-secret"),
    ("https://datadryad.org:fixture-port-secret/file", "fixture-port-secret"),
    ("https://[fixture-malformed-secret/", "fixture-malformed-secret"),
]


@pytest.mark.parametrize("url,secret", CASES)
def test_policy_rejection_does_not_echo_sensitive_locator_values(url, secret):
    with pytest.raises(ValueError) as rejected:
        validate_download_url(url)
    assert secret not in str(rejected.value)
    assert url not in str(rejected.value)


@pytest.mark.parametrize("url,secret", CASES)
@pytest.mark.parametrize("metadata_only", [False, True])
def test_refused_provider_download_cannot_publish_sensitive_locator(
    tmp_path, monkeypatch, url, secret, metadata_only
):
    # Network metadata is an I/O fixture; actual admission/error/catalog code runs.
    metadata = {
        "doi": "10.6084/m9.figshare.123.v1",
        "files": [
            {"id": 1, "name": "features.csv", "size": 12, "download_url": url},
        ],
    }
    monkeypatch.setattr(empirical_fetch, "read_json", lambda _: metadata)
    dataset = {
        "dataset_id": "fixture",
        "doi": "10.6084/m9.figshare.123",
        "title": "fixture",
        "source_url": "https://figshare.com/articles/dataset/fixture/123",
    }
    rows = empirical_fetch._process_figshare_dataset(
        dataset, tmp_path, metadata_only=metadata_only, force=False
    )
    assert rows[0]["file_downloaded"] is False
    assert rows[0]["download_url"] is None
    assert secret not in json.dumps(rows)


def test_malformed_provider_locator_preserves_following_metadata_rows(tmp_path, monkeypatch):
    metadata = {
        "doi": "10.6084/m9.figshare.123.v1",
        "files": [
            {"id": 1, "name": "bad.csv", "size": 12, "download_url": "https://[invalid/"},
            {
                "id": 2,
                "name": "features.csv",
                "size": 12,
                "download_url": "https://ndownloader.figshare.com/files/2",
            },
        ],
    }
    monkeypatch.setattr(empirical_fetch, "read_json", lambda _: metadata)
    rows = empirical_fetch._process_figshare_dataset(
        {
            "dataset_id": "fixture",
            "doi": metadata["doi"],
            "title": "fixture",
            "source_url": "https://figshare.com/articles/dataset/fixture/123",
        },
        tmp_path,
        metadata_only=True,
        force=False,
    )
    assert rows[0]["file_error"] and rows[0]["download_url"] is None
    assert not rows[0]["file_downloaded"]
    assert rows[1]["path"] == "features.csv" and rows[1]["file_error"] is None
    assert rows[1]["download_url"] == metadata["files"][1]["download_url"]
