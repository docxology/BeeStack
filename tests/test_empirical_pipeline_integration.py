"""Current-process coverage for data-gated empirical BeeBrain paths."""

from __future__ import annotations

import json
import urllib.error
from pathlib import Path

import pytest

from beestack.brain import empirical_fetch
from beestack.brain.empirical_pipeline import build_empirical_analysis_bundle
from beestack.config import BeeStackConfig
from beestack.source_refresh import (
    ExternalDatasetRecord,
    SourceRefreshRecord,
    source_refresh_markdown,
    source_refresh_payload,
)
from beestack.visualization import generate_empirical_figures
from beestack.visualization.connectome_figures import generate_connectome_figures

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_local_empirical_bundle_and_figures_cover_parsers(tmp_path: Path) -> None:
    source_dir = PROJECT_ROOT / "output" / "data" / "empirical_sources"
    if not source_dir.exists():
        pytest.skip("local empirical source payloads are absent")

    bundle = build_empirical_analysis_bundle(BeeStackConfig(), PROJECT_ROOT)

    assert bundle is not None
    assert len(bundle.panels) >= 1
    assert bundle.anatomy_summary.dataset_id == "virtual-honeybee-standard-brain"
    assert bundle.connectome_report.tier == "structural_projectome"
    assert bundle.data_completeness.parseable_fraction >= 0.0

    empirical_dir = tmp_path / "figures" / "empirical"
    empirical_paths = generate_empirical_figures(
        bundle.panels,
        bundle.stats,
        bundle.alignment,
        empirical_dir,
        antennal_summaries=bundle.antennal_summaries,
        anatomy_summary=bundle.anatomy_summary,
        anatomy_inventories=bundle.anatomy_inventories,
        neuropil_abbreviations=bundle.neuropil_abbreviations,
        activity_summary=bundle.activity_summary,
        waggle_summary=bundle.waggle_dataset.summary if bundle.waggle_dataset is not None else None,
        data_completeness=bundle.data_completeness,
        connectome_report=bundle.connectome_report,
    )
    connectome_paths = generate_connectome_figures(
        bundle.connectome_report,
        empirical_dir,
        completeness_tiers=bundle.data_completeness.connectome_tiers,
    )

    assert len(empirical_paths) >= 10
    assert len(connectome_paths) == 3
    for path in (*empirical_paths, *connectome_paths):
        assert path.is_file()
        assert path.with_suffix(".json").is_file()
        assert path.with_name(f"{path.stem}_data.json").is_file()


def test_fetch_empirical_sources_metadata_only_catalogs_without_network(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_read_json(url: str) -> dict[str, object]:
        if url.startswith(empirical_fetch.FIGSHARE_API_ROOT):
            return {
                "doi": "10.6084/m9.figshare.24715977.v1",
                "license": {"name": "CC BY 4.0", "url": "https://creativecommons.org"},
                "files": [
                    {
                        "name": "features.csv",
                        "size": 128,
                        "mime_type": "text/csv",
                        "download_url": (
                            "https://s3-eu-west-1.amazonaws.com/"
                            "pfigshare-u-files/44977549/features.csv"
                        ),
                    }
                ],
            }
        if url.endswith("/files"):
            return {
                "_embedded": {
                    "stash:files": [
                        {
                            "path": "ReadMe.md",
                            "size": 64,
                            "mimeType": "text/markdown",
                            "_links": {
                                "stash:download": {
                                    "href": "/api/v2/files/1/download",
                                }
                            },
                        }
                    ]
                }
            }
        if url.startswith(empirical_fetch.DRYAD_API_ROOT):
            return {
                "storageSize": 256,
                "_links": {"stash:version": {"href": "/api/v2/versions/1"}},
            }
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(empirical_fetch, "read_json", fake_read_json)

    summary = empirical_fetch.fetch_empirical_sources(tmp_path, metadata_only=True)
    catalog = json.loads((tmp_path / "catalog.json").read_text(encoding="utf-8"))
    archives = json.loads((tmp_path / "archives.json").read_text(encoding="utf-8"))
    anatomy = json.loads((tmp_path / "anatomy_downloads.json").read_text(encoding="utf-8"))

    assert summary.catalog_count == len(catalog)
    assert summary.downloaded_archives == 0
    assert summary.downloaded_files == 0
    assert summary.downloaded_anatomy == 0
    assert archives
    assert anatomy
    assert any(row["parser_status"].startswith("citation_anchor_only") for row in catalog)
    assert any(row["source_repository"] == "figshare" for row in catalog)
    assert any(row["source_repository"] == "dryad" for row in catalog)


def test_source_refresh_markdown_records_verified_and_discovery_sources() -> None:
    payload = source_refresh_payload(PROJECT_ROOT)
    markdown = source_refresh_markdown(PROJECT_ROOT)

    assert payload["schema"] == "beestack.source_refresh.v2"
    assert payload["direct_verification_required"] is True
    assert any(row["citation_key"] == "vaxenburg2025flybody" for row in payload["records"])
    assert "Perplexity Discovery Candidates Not Promoted" in markdown
    assert "`@vaxenburg2025flybody`" in markdown
    assert "These candidates remain discovery records, not manuscript evidence." in markdown


def test_source_refresh_records_validate_required_contracts() -> None:
    with pytest.raises(ValueError, match="section_targets"):
        SourceRefreshRecord(
            citation_key="bad",
            title="Bad record",
            authors="Example",
            year=2026,
            doi="10.1000/example",
            source_url="https://doi.org/10.1000/example",
            direct_verification_status="verified",
            discovery_channel="test",
            claim_tier="method_anchor",
            availability_status="metadata",
            section_targets=(),
            figure_targets=("output/figures/example.png",),
            notes="invalid section targets",
        )
    with pytest.raises(ValueError, match="malformed"):
        SourceRefreshRecord(
            citation_key="bad",
            title="Bad record",
            authors="Example",
            year=2026,
            doi="not-a-doi",
            source_url="https://example.org",
            direct_verification_status="verified",
            discovery_channel="test",
            claim_tier="method_anchor",
            availability_status="metadata",
            section_targets=("manuscript/01.md",),
            figure_targets=("output/figures/example.png",),
            notes="invalid doi",
        )
    with pytest.raises(ValueError, match="directly verified"):
        SourceRefreshRecord(
            citation_key="bad",
            title="Bad record",
            authors="Example",
            year=2026,
            doi="10.1000/example",
            source_url="https://doi.org/10.1000/example",
            direct_verification_status="discovery",
            discovery_channel="test",
            claim_tier="method_anchor",
            availability_status="metadata",
            section_targets=("manuscript/01.md",),
            figure_targets=("output/figures/example.png",),
            notes="invalid verification",
        )
    with pytest.raises(ValueError, match="unsupported"):
        SourceRefreshRecord(
            citation_key="bad",
            title="Bad record",
            authors="Example",
            year=2026,
            doi="10.1000/example",
            source_url="https://doi.org/10.1000/example",
            direct_verification_status="verified",
            discovery_channel="test",
            claim_tier="unsupported",
            availability_status="metadata",
            section_targets=("manuscript/01.md",),
            figure_targets=("output/figures/example.png",),
            notes="invalid tier",
        )
    with pytest.raises(ValueError, match="resource_id"):
        ExternalDatasetRecord(
            resource_id="",
            name="Dataset",
            resource_type="archive",
            official_doi="10.1000/example",
            official_url="https://example.org",
            target_module="BeeBrain",
            wired_in_beestack=False,
            blocker="not wired",
        )
    with pytest.raises(ValueError, match="malformed"):
        ExternalDatasetRecord(
            resource_id="dataset",
            name="Dataset",
            resource_type="archive",
            official_doi="bad-doi",
            official_url="https://example.org",
            target_module="BeeBrain",
            wired_in_beestack=False,
            blocker="not wired",
        )
    with pytest.raises(ValueError, match="DOI or HTTPS"):
        ExternalDatasetRecord(
            resource_id="dataset",
            name="Dataset",
            resource_type="archive",
            official_doi="",
            official_url="ftp://example.org/data",
            target_module="BeeBrain",
            wired_in_beestack=False,
            blocker="not wired",
        )


def test_empirical_fetch_oauth_and_json_response_helpers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class JsonResponse:
        def __init__(self, payload: dict[str, object], url: str) -> None:
            self._payload = json.dumps(payload).encode("utf-8")
            self._url = url

        def read(self, _size: int = -1) -> bytes:
            return self._payload

        def geturl(self) -> str:
            return self._url

        def __enter__(self) -> JsonResponse:
            return self

        def __exit__(self, *_exc: object) -> None:
            return None

    def fake_urlopen(request: object, timeout: float) -> JsonResponse:
        url = getattr(request, "full_url", "")
        if url.endswith("/oauth/token"):
            return JsonResponse({"access_token": "oauth-token"}, url)
        return JsonResponse({"ok": True}, url)

    monkeypatch.delenv("DRYAD_API_TOKEN", raising=False)
    monkeypatch.setenv("DRYAD_CLIENT_ID", "client")
    monkeypatch.setenv("DRYAD_CLIENT_SECRET", "secret")
    monkeypatch.setattr(empirical_fetch.urllib.request, "urlopen", fake_urlopen)

    assert empirical_fetch._dryad_oauth_token() == "oauth-token"
    assert empirical_fetch._dryad_auth_headers()["Authorization"] == "Bearer oauth-token"
    assert empirical_fetch.read_json("https://datadryad.org/api/v2/datasets/example") == {
        "ok": True
    }


def test_empirical_fetch_download_helpers_and_branch_records(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class ChunkResponse:
        def __init__(self, chunks: list[bytes], url: str) -> None:
            self._chunks = iter(chunks)
            self._url = url

        def read(self, _size: int = -1) -> bytes:
            return next(self._chunks, b"")

        def geturl(self) -> str:
            return self._url

        def __enter__(self) -> ChunkResponse:
            return self

        def __exit__(self, *_exc: object) -> None:
            return None

    monkeypatch.setenv("DRYAD_API_TOKEN", "dryad-token")
    dryad_headers = empirical_fetch._download_headers_for_url(
        "https://datadryad.org/api/v2/files/1/download"
    )
    figshare_headers = empirical_fetch._download_headers_for_url("https://figshare.com/file")
    assert dryad_headers["Authorization"] == "Bearer dryad-token"
    assert "Authorization" not in figshare_headers
    assert empirical_fetch._dryad_download_remediation("401 Unauthorized").startswith(
        "401 Unauthorized"
    )
    assert "dataset exceeds Dryad zip limit" in empirical_fetch._dryad_download_remediation(
        "405 too large for zip"
    )

    streamed = tmp_path / "streamed.bin"
    empirical_fetch._stream_response_to_path(
        ChunkResponse([b"bee", b"stack"], "https://figshare.com/file"),
        streamed,
    )
    assert streamed.read_bytes() == b"beestack"
    assert empirical_fetch.sha256_file(streamed) == (
        "7f72c02c8c31fe44a2e753083202e4a293a6bd619669eab721ccb685210f9de2"
    )

    def fake_open_validated_response(*_args: object, **_kwargs: object) -> ChunkResponse:
        return ChunkResponse([b"payload"], "https://figshare.com/file")

    monkeypatch.setattr(empirical_fetch, "_open_validated_response", fake_open_validated_response)
    downloaded = tmp_path / "downloads" / "payload.bin"
    empirical_fetch.download_url("https://figshare.com/file", downloaded)
    assert downloaded.read_bytes() == b"payload"

    class RedirectOpener:
        def open(self, request: object, timeout: float) -> None:
            raise urllib.error.HTTPError(
                getattr(request, "full_url", "https://datadryad.org/api/v2/files/1/download"),
                302,
                "Found",
                {"Location": "https://dryad-assetstore-example.amazonaws.com/payload"},
                None,
            )

    monkeypatch.setattr(
        empirical_fetch.urllib.request,
        "build_opener",
        lambda *_handlers: RedirectOpener(),
    )
    monkeypatch.setattr(
        empirical_fetch.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: ChunkResponse(
            [b"redirected"], "https://dryad-assetstore-example.amazonaws.com/payload"
        ),
    )
    redirected = tmp_path / "redirected.bin"
    empirical_fetch._download_presigned_redirect(
        "https://datadryad.org/api/v2/files/1/download",
        redirected,
        auth_headers={"User-Agent": empirical_fetch.USER_AGENT, "Authorization": "Bearer token"},
    )
    assert redirected.read_bytes() == b"redirected"

    def fake_download_url(url: str, path: Path) -> None:
        if "blocked" in url:
            raise urllib.error.URLError("offline")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("source rows\n", encoding="utf-8")

    monkeypatch.setattr(empirical_fetch, "download_url", fake_download_url)
    supplement_rows = empirical_fetch._process_publisher_supplement_dataset(
        {
            "dataset_id": "publisher-supplement",
            "doi": "10.1371/example",
            "title": "Publisher supplement",
            "source_url": "https://example.org/source",
            "license_note": "open",
            "supplementary_downloads": (
                ("ok.csv", "https://mdpi-res.com/ok.csv"),
                ("blocked.csv", "https://mdpi-res.com/blocked.csv"),
            ),
        },
        tmp_path,
        metadata_only=False,
        force=True,
    )
    assert [row["file_downloaded"] for row in supplement_rows] == [True, False]
    assert supplement_rows[0]["parser_status"] == "supported_publisher_supplement"
    assert supplement_rows[1]["parser_status"] == "download_blocked"

    monkeypatch.setattr(
        empirical_fetch,
        "read_json",
        lambda _url: {
            "doi": "10.6084/m9.figshare.1.v1",
            "license": {"name": "CC BY", "url": "https://creativecommons.org"},
            "files": [
                {
                    "name": "features.csv",
                    "size": 7,
                    "mime_type": "text/csv",
                    "download_url": "https://figshare.com/file/features.csv",
                }
            ],
        },
    )
    figshare_rows = empirical_fetch._process_figshare_dataset(
        {
            "dataset_id": "figshare-example",
            "doi": "10.6084/m9.figshare.1.v1",
            "title": "Figshare example",
            "source_url": "https://figshare.com/articles/dataset/example/1",
            "license_note": "catalog license",
        },
        tmp_path,
        metadata_only=False,
        force=True,
    )
    assert figshare_rows[0]["file_downloaded"] is True
    assert figshare_rows[0]["parser_status"] == "supported_csv"
