"""Synthetic acquisition metadata/HTTP bytes, isolated in tmp_path, never evidence."""

from __future__ import annotations

import hashlib
import http.client
import json
import urllib.error
import urllib.request
import zipfile
from dataclasses import replace
from io import BytesIO

import pytest

from beestack.brain import anatomy, empirical_fetch
from beestack.brain.datasets import BeeBrainAtlasAsset
from beestack.security import completed_download, completion_path
from beestack.security.path_safety import download_source_identity


class _ByteSocket:
    def __init__(self, data):
        self.stream = BytesIO(data)

    def makefile(self, *_args):
        return self.stream


def _http_response(body, url, declared=None, *, status=200, headers=None):
    length = len(body) if declared is None else declared
    header_bytes = "".join(f"{key}: {value}\r\n" for key, value in (headers or {}).items())
    wire = f"HTTP/1.1 {status} Fixture\r\nContent-Length: {length}\r\n{header_bytes}\r\n"
    response = http.client.HTTPResponse(_ByteSocket(wire.encode() + body))
    response.begin()
    response.url = url
    response.msg = response.reason
    return response


@pytest.fixture
def transport(monkeypatch):
    """Replace only HTTPS I/O; real request, response and JSON parsers still run."""
    routes = {}
    requests = []
    original = urllib.request.build_opener

    class FixtureHTTPS(urllib.request.HTTPSHandler):
        def https_open(self, request):
            requests.append(request.full_url)
            result = routes[request.full_url]
            if isinstance(result, BaseException):
                raise result
            if isinstance(result, dict):
                return _http_response(json.dumps(result).encode(), request.full_url)
            if isinstance(result, tuple):
                if isinstance(result[0], int):
                    return _http_response(
                        result[2], request.full_url, status=result[0], headers=result[1]
                    )
                return _http_response(result[0], request.full_url, declared=result[1])
            return _http_response(result, request.full_url)

    monkeypatch.setattr(
        urllib.request, "build_opener", lambda *handlers: original(*handlers, FixtureHTTPS())
    )
    monkeypatch.delenv("DRYAD_API_TOKEN", raising=False)
    monkeypatch.delenv("DRYAD_CLIENT_ID", raising=False)
    monkeypatch.delenv("DRYAD_CLIENT_SECRET", raising=False)
    return routes, requests


def _zip_bytes():
    output = BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("synthetic-fixture.csv", "value\n1\n")
    return output.getvalue()


@pytest.mark.parametrize("changed", ["download_url", "doi", "size"])
@pytest.mark.parametrize("force", [False, True])
def test_figshare_changed_source_failed_refresh_never_relabels_cache(
    tmp_path, transport, changed, force
):
    routes, requests = transport
    dataset = {
        "dataset_id": "synthetic-figshare",
        "doi": "10.6084/m9.figshare.1.v1",
        "title": "Synthetic fixture, not empirical evidence",
        "source_url": "https://figshare.com/articles/dataset/fixture/1",
    }
    url_a = "https://figshare.com/file/features.csv?token=private-A"
    payload = {
        "doi": dataset["doi"],
        "files": [{"name": "features.csv", "size": 8, "download_url": url_a}],
    }
    routes[empirical_fetch.figshare_article_url(dataset)] = payload
    routes[url_a] = b"value\n1\n"

    def fetch(refresh=False):
        return empirical_fetch._process_figshare_dataset(
            dataset, tmp_path, metadata_only=False, force=refresh
        )[0]

    first = fetch()
    path = tmp_path / dataset["dataset_id"] / "files/features.csv"
    original_marker = completion_path(path).read_bytes()
    identity_a = download_source_identity(url_a, doi=payload["doi"], size=8)
    assert first["file_downloaded"]
    assert completed_download(path, source_identity=identity_a)
    requests.clear()
    assert fetch()["file_downloaded"]
    assert requests == [empirical_fetch.figshare_article_url(dataset)]

    if changed == "doi":
        payload["doi"] = "10.6084/m9.figshare.1.v2"
    elif changed == "size":
        payload["files"][0]["size"] = 9
    else:
        payload["files"][0]["download_url"] = url_a.replace("private-A", "private-B")
    url_b = payload["files"][0]["download_url"]
    routes[url_b] = (b"short", 20)
    failed = fetch(refresh=force)
    identity_b = download_source_identity(
        url_b, doi=payload["doi"], size=payload["files"][0]["size"]
    )
    assert identity_a != identity_b
    assert failed["doi"] == payload["doi"]
    assert not failed["file_downloaded"]
    assert failed["local_file"] is None
    assert failed["file_sha256"] is None
    assert "incomplete response" in failed["file_error"]
    assert path.read_bytes() == b"value\n1\n"
    assert completion_path(path).read_bytes() == original_marker
    assert completed_download(path)
    assert completed_download(path, source_identity=identity_a)
    assert not completed_download(path, source_identity=identity_b)
    assert empirical_fetch._needs_download(
        path, force=False, metadata_only=False, source_identity=identity_b
    )

    routes[url_b] = b"value\n2\n"
    successful = fetch()
    assert successful["file_downloaded"]
    assert path.read_bytes() == b"value\n2\n"
    assert completed_download(path, source_identity=identity_b)
    assert not completed_download(path, source_identity=identity_a)
    marker = json.loads(completion_path(path).read_text())
    assert set(marker) == {"size", "sha256", "source_identity"}
    assert "private-" not in completion_path(path).read_text()
    assert marker["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("changed", ["url", "doi", "size"])
def test_dryad_individual_file_cache_requires_advertised_source(tmp_path, transport, changed):
    routes, requests = transport
    dataset = {"dataset_id": "synthetic-dryad", "doi": "10.5061/dryad.fixture", "title": "Fixture"}
    file_row = {
        "path": "fixture.csv",
        "size": 8,
        "_links": {"stash:download": {"href": "/api/v2/files/1/download"}},
    }
    url_a = "https://datadryad.org/api/v2/files/1/download"
    routes[url_a] = b"value\n1\n"

    def fetch():
        return empirical_fetch._process_dryad_files(
            dataset,
            [file_row],
            tmp_path,
            metadata_only=False,
            force=False,
            archive_path=None,
            archive_downloaded=False,
            archive_download_url=None,
            archive_expected_size_bytes=None,
        )[0][0]

    assert fetch()["file_downloaded"]
    requests.clear()
    assert fetch()["file_downloaded"]
    assert requests == []
    path = tmp_path / dataset["dataset_id"] / "files/fixture.csv"
    marker = completion_path(path).read_bytes()
    if changed == "url":
        file_row["_links"]["stash:download"]["href"] = "/api/v2/files/2/download"
    elif changed == "doi":
        dataset["doi"] = "10.5061/dryad.changed"
    else:
        file_row["size"] = 9
    url_b = "https://datadryad.org" + file_row["_links"]["stash:download"]["href"]
    routes[url_b] = urllib.error.URLError("synthetic transport failure")
    row = fetch()
    assert requests == [url_b]
    assert not row["file_downloaded"]
    assert row["local_file"] is None
    assert completion_path(path).read_bytes() == marker
    assert path.read_bytes() == b"value\n1\n"


def test_dryad_archive_version_identity_survives_failed_atomic_refresh(tmp_path, transport):
    routes, requests = transport
    dataset = {"dataset_id": "synthetic-dryad", "doi": "10.5061/dryad.fixture", "title": "Fixture"}
    metadata_url = empirical_fetch.dryad_dataset_url(dataset["doi"])
    metadata = {"storageSize": 1000, "_links": {"stash:version": {"href": "/api/v2/versions/1"}}}
    routes[metadata_url] = metadata
    for version in (1, 2):
        routes[f"https://datadryad.org/api/v2/versions/{version}/files"] = {
            "_embedded": {"stash:files": []}
        }
    url_a = "https://datadryad.org/api/v2/versions/1/download"
    url_b = "https://datadryad.org/api/v2/versions/2/download"
    data_a = _zip_bytes()
    routes[url_a] = data_a

    def fetch(force=False):
        return empirical_fetch._process_dryad_dataset(
            dataset, tmp_path, metadata_only=False, force=force
        )[1]

    first = fetch()
    path = tmp_path / dataset["dataset_id"] / "synthetic-dryad.zip"
    marker_a = completion_path(path).read_bytes()
    assert first["archive_downloaded"]
    assert first["archive_expected_size_bytes"] == 1000
    assert first["archive_download_url"] == url_a
    assert first["archive_size_bytes"] == len(data_a)  # Catalog size is not an exact ZIP length.
    requests.clear()
    assert fetch()["archive_skipped_existing"]
    assert url_a not in requests
    metadata["_links"]["stash:version"]["href"] = "/api/v2/versions/2"
    routes[url_b] = (b"short", 100)
    failed = fetch(force=True)
    assert not failed["archive_downloaded"]
    assert not failed["archive_skipped_existing"]
    assert failed["local_archive"] is None
    assert failed["archive_download_url"] == url_b
    assert completion_path(path).read_bytes() == marker_a
    assert path.read_bytes() == data_a
    assert completed_download(
        path, source_identity=download_source_identity(url_a, doi=dataset["doi"], size=1000)
    )
    routes[url_b] = data_a
    assert fetch()["archive_downloaded"]
    assert completed_download(
        path, source_identity=download_source_identity(url_b, doi=dataset["doi"], size=1000)
    )
    routes[metadata_url] = urllib.error.URLError("metadata unavailable")
    missing = fetch()
    assert missing["archive_download_url"] is None
    assert not missing["archive_downloaded"]
    assert path.read_bytes() == data_a


@pytest.mark.parametrize("changed", ["url", "size"])
def test_anatomy_records_use_same_approximate_catalog_identity(tmp_path, transport, changed):
    routes, requests = transport
    asset = BeeBrainAtlasAsset(
        asset_id="synthetic-atlas",
        title="Synthetic fixture",
        url="https://www.bcp.fu-berlin.de/fixture.zip",
        file_name="fixture.zip",
        size_bytes=1000,
        asset_type="archive",
        description="Synthetic fixture only",
    )
    dataset = {"dataset_id": "synthetic-anatomy", "assets": [asset.as_dict()]}
    routes[asset.url] = _zip_bytes()

    def fetch(force=False):
        return empirical_fetch._process_anatomy_dataset(
            dataset, tmp_path, metadata_only=False, force=force
        )[0]

    first = fetch()
    path = tmp_path / dataset["dataset_id"] / asset.file_name
    assert first["downloaded"]
    assert first["size_bytes"] != first["expected_size_bytes"]
    assert anatomy.atlas_inventory_from_zip(path).file_count == 1
    requests.clear()
    assert fetch()["skipped_existing"]
    assert requests == []
    changed_asset = (
        replace(asset, url=asset.url.replace("fixture.zip", "changed.zip"))
        if changed == "url"
        else replace(asset, size_bytes=1001)
    )
    dataset["assets"] = [changed_asset.as_dict()]
    routes[changed_asset.url] = (b"short", 20)
    marker_a = completion_path(path).read_bytes()
    failed = fetch(force=True)
    assert not failed["downloaded"]
    assert not failed["skipped_existing"]
    assert failed["sha256"] is None
    assert completion_path(path).read_bytes() == marker_a
    assert anatomy.atlas_download_record_from_asset("fixture", asset, path).downloaded
    assert not anatomy.atlas_download_record_from_asset("fixture", changed_asset, path).downloaded


def test_publisher_unknown_size_and_doi_are_stable_acquisition_metadata(tmp_path, transport):
    routes, requests = transport
    url = "https://mdpi-res.com/fixture.csv"
    routes[url] = b"value\n1\n"
    dataset = {
        "dataset_id": "synthetic-publisher",
        "doi": "10.1371/fixture",
        "title": "Fixture",
        "supplementary_downloads": [("fixture.csv", url)],
    }

    def fetch():
        return empirical_fetch._process_publisher_supplement_dataset(
            dataset, tmp_path, metadata_only=False, force=False
        )[0]

    first = fetch()
    assert first["file_downloaded"]
    assert first["size"] is None
    path = tmp_path / dataset["dataset_id"] / "supplementary/fixture.csv"
    assert completed_download(
        path, source_identity=download_source_identity(url, doi=first["doi"], size=first["size"])
    )
    requests.clear()
    assert fetch()["file_downloaded"]
    assert requests == []
    dataset["doi"] = "10.1371/changed"
    routes[url] = urllib.error.URLError("synthetic transport failure")
    assert not fetch()["file_downloaded"]
    assert path.read_bytes() == b"value\n1\n"


@pytest.mark.parametrize("receipt", [None, "legacy", "nonobject"])
def test_unbound_legacy_bytes_are_preserved_not_auto_sealed(tmp_path, receipt):
    path = tmp_path / "fixture.csv"
    data = b"value\n1\n"
    path.write_bytes(data)
    if receipt is not None:
        record = (
            {"size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            if receipt == "legacy"
            else []
        )
        completion_path(path).write_text(json.dumps(record))
    expected = download_source_identity("https://figshare.com/file", doi="10.1/fixture", size=8)
    assert completed_download(path) == (receipt == "legacy")
    assert not completed_download(path, source_identity=expected)
    assert empirical_fetch._needs_download(
        path, force=False, metadata_only=False, source_identity=expected
    )
    assert not empirical_fetch._needs_download(
        path, force=False, metadata_only=True, source_identity=expected
    )
    assert path.read_bytes() == data
    assert completion_path(path).exists() == (receipt is not None)


def test_url_only_helper_binds_requested_url_not_redirect_target(tmp_path, transport):
    routes, requests = transport
    url = "https://figshare.com/file?signature=fixture-secret"
    target = "https://ndownloader.figshare.com/files/1"
    routes[url] = (302, {"Location": target}, b"")
    routes[target] = b"value\n1\n"
    path = tmp_path / "fixture.csv"
    empirical_fetch.download_url(url, path)
    assert requests == [url, target]
    assert not completed_download(path, source_identity=download_source_identity(target))
    expected = download_source_identity(url)
    assert completed_download(path, source_identity=expected)
    assert not completed_download(path, source_identity=download_source_identity(url + "-changed"))
    assert "fixture-secret" not in completion_path(path).read_text()
    assert expected == download_source_identity(
        "https://FIGSHARE.COM:443/file?signature=fixture-secret#ignored"
    )
    path.write_bytes(b"tampered")
    assert not completed_download(path, source_identity=expected)
