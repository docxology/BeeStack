"""Real byte-backed transport and hostile scientific container regressions."""

from __future__ import annotations

import http.client
import urllib.request
import zipfile
from io import BytesIO

import h5py
import numpy as np
import pytest
from openpyxl import Workbook
from scipy.io import savemat

from beestack.brain import anatomy, empirical_fetch
from beestack.brain.connectome import structural_wiring
from beestack.brain.empirical_data import ArrayLimits
from beestack.brain.empirical_parsers.antennal import antennal_summaries_from_archive
from beestack.brain.empirical_parsers.calcium import (
    calcium_dataset_from_mat_bytes,
    calcium_datasets_from_archive,
    load_hdf5_mat_payload,
    validate_mat_v5,
    validate_paoli_normalization,
)
from beestack.brain.empirical_parsers.common import (
    WorkbookLimits,
    iter_xlsx_members,
    validate_workbook,
)
from beestack.brain.empirical_parsers.panels import (
    dataframe_summaries_from_workbook,
    load_empirical_panels,
    panels_from_workbook,
    workbook_dataframe_summaries,
)
from beestack.security import ArchiveBudget, IntakePolicyError, completed_download


class ByteSocket:
    def __init__(self, data):
        self.stream = BytesIO(data)

    def makefile(self, *_args):
        return self.stream


def response(body, *, declared=None, extra=b"", status=b"200 OK", url="https://figshare.com/a"):
    length = b"" if declared is None else f"Content-Length: {declared}\r\n".encode()
    result = http.client.HTTPResponse(
        ByteSocket(b"HTTP/1.1 " + status + b"\r\n" + length + extra + b"\r\n" + body)
    )
    result.begin()
    result.url = url
    result.msg = result.reason
    return result


def archive_bytes(entries):
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries:
            archive.writestr(name, data)
    return stream.getvalue()


def workbook_bytes(cell="B2", *, dimension=None):
    workbook = Workbook()
    sheet = workbook.active
    sheet["A1"] = "stimulus"
    sheet["B1"] = "response"
    sheet["A2"] = "odor1"
    sheet[cell] = 1.0
    sheet["A3"] = "odor2"
    sheet["B3"] = 2.0
    output = BytesIO()
    workbook.save(output)
    workbook.close()
    data = output.getvalue()
    if dimension is not None:
        entries = []
        with zipfile.ZipFile(BytesIO(data)) as archive:
            for info in archive.infolist():
                payload = archive.read(info)
                if info.filename == "xl/worksheets/sheet1.xml":
                    import re

                    payload = re.sub(rb'<dimension ref="[^"]*"/>', dimension, payload)
                entries.append((info.filename, payload))
        data = archive_bytes(entries)
    return data


def test_real_http_short_eof_does_not_certify_cache(tmp_path):
    path = tmp_path / "features.csv"
    with (
        response(b"bee", declared=12) as source,
        pytest.raises(IntakePolicyError, match="incomplete"),
    ):
        empirical_fetch._stream_response_to_path(source, path)
    assert not path.exists()
    assert empirical_fetch._needs_download(path, force=False, metadata_only=False)
    assert list(tmp_path.iterdir()) == []


def test_failed_refresh_preserves_completed_cache_and_marker(tmp_path):
    path = tmp_path / "data"
    with response(b"complete", declared=8) as source:
        empirical_fetch._stream_response_to_path(source, path)
    assert completed_download(path)
    with response(b"short", declared=20) as source, pytest.raises(IntakePolicyError):
        empirical_fetch._stream_response_to_path(source, path)
    assert path.read_bytes() == b"complete"
    assert completed_download(path)
    assert not empirical_fetch._needs_download(path, force=False, metadata_only=False)


def test_real_chunk_interruption_leaves_no_partial_file(tmp_path):
    chunks = b"4\r\nbees\r\n8\r\ncut"
    source = response(chunks, extra=b"Transfer-Encoding: chunked\r\n")
    with source, pytest.raises(http.client.IncompleteRead):
        empirical_fetch._stream_response_to_path(source, tmp_path / "data")
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "body,declared,accepted", [(b"bees", 4, True), (b"bees!", None, False), (b"bees!", 5, False)]
)
def test_response_actual_and_declared_caps(tmp_path, body, declared, accepted):
    path = tmp_path / "data"
    with response(body, declared=declared) as source:
        if accepted:
            empirical_fetch._stream_response_to_path(source, path, max_bytes=4)
            assert path.read_bytes() == body
        else:
            with pytest.raises(IntakePolicyError):
                empirical_fetch._stream_response_to_path(source, path, max_bytes=4)
            assert not path.exists()


def test_small_declared_length_clips_real_http_response(tmp_path):
    with response(b"beesEXTRA", declared=4) as source:
        empirical_fetch._stream_response_to_path(source, tmp_path / "data", max_bytes=4)
    assert (tmp_path / "data").read_bytes() == b"bees"


def test_metadata_and_operation_byte_budgets(monkeypatch, tmp_path):
    monkeypatch.setattr(empirical_fetch, "MAX_METADATA_BYTES", 4)
    with response(b'{"x": 1}') as source, pytest.raises(IntakePolicyError):
        empirical_fetch._response_json(source)
    token = empirical_fetch._TRANSFER_BUDGET.set(empirical_fetch.TransferBudget(max_bytes=6))
    try:
        with response(b"bees") as source:
            empirical_fetch._stream_response_to_path(source, tmp_path / "one", max_bytes=4)
        with response(b"bees") as source, pytest.raises(IntakePolicyError, match="operation"):
            empirical_fetch._stream_response_to_path(source, tmp_path / "two", max_bytes=4)
    finally:
        empirical_fetch._TRANSFER_BUDGET.reset(token)
    assert completed_download(tmp_path / "one")
    assert not (tmp_path / "two").exists()


@pytest.mark.parametrize("code", [301, 302, 303, 307, 308])
def test_redirect_decisions_validate_and_strip_cross_origin_before_dispatch(code):
    handler = empirical_fetch.ValidatedRedirectHandler()
    request = urllib.request.Request(
        "https://datadryad.org/api/a",
        headers={"Authorization": "Bearer sentinel", "Cookie": "secret"},
    )
    same = handler.redirect_request(request, BytesIO(), code, "redirect", {}, "../b")
    assert same.full_url == "https://datadryad.org/b"
    assert same.get_header("Authorization") == "Bearer sentinel"
    cross = handler.redirect_request(
        request,
        BytesIO(),
        code,
        "redirect",
        {},
        "https://s3-eu-west-1.amazonaws.com/pfigshare-u-files/a",
    )
    assert cross.get_header("Authorization") is None
    assert cross.get_header("Cookie") is None
    for target in ("http://127.0.0.1/action", "https://unlisted.invalid/a"):
        body = BytesIO()
        with pytest.raises(ValueError):
            handler.redirect_request(request, body, code, "redirect", {}, target)
        assert body.closed


def test_real_opener_rejects_intermediate_hop_before_dispatch(monkeypatch):
    dispatched = []

    class RecordingHTTPS(urllib.request.HTTPSHandler):
        def https_open(self, request):
            dispatched.append(request.full_url)
            return response(
                b"",
                declared=0,
                status=b"302 Found",
                extra=b"Location: https://unlisted.invalid/a\r\n",
                url=request.full_url,
            )

    original = urllib.request.build_opener
    monkeypatch.setattr(
        urllib.request, "build_opener", lambda *handlers: original(*handlers, RecordingHTTPS())
    )
    monkeypatch.setenv("DRYAD_API_TOKEN", "sentinel")
    with pytest.raises(ValueError):
        empirical_fetch._open_validated_response(
            "https://datadryad.org/api/a", context="test", timeout=1
        )
    assert dispatched == ["https://datadryad.org/api/a"]


@pytest.mark.parametrize("code", [302, 307])
def test_oauth_redirects_are_closed_and_never_replayed(code):
    request = urllib.request.Request(
        "https://datadryad.org/oauth/token", data=b"client_secret=sentinel"
    )
    body = BytesIO()
    with pytest.raises(ValueError, match="credential exchange"):
        empirical_fetch.ValidatedRedirectHandler().redirect_request(
            request, body, code, "redirect", {}, "https://figshare.com/a"
        )
    assert body.closed


def test_nested_archive_budget_is_shared_and_irrelevant_payload_is_not_expanded():
    workbook = workbook_bytes()
    inner = archive_bytes([("one.xlsx", workbook)])
    with zipfile.ZipFile(BytesIO(workbook)) as package:
        package_bytes = sum(info.file_size for info in package.infolist())
    one_branch = len(inner) + len(workbook) + package_bytes
    tree = archive_bytes([("one.zip", inner), ("two.zip", inner), ("irrelevant.bin", b"x" * 10000)])
    with zipfile.ZipFile(BytesIO(tree)) as archive:
        iterator = iter_xlsx_members(archive, budget=ArchiveBudget(max_bytes=one_branch))
        assert next(iterator)[0] == "one.zip/one.xlsx"
        with pytest.raises(IntakePolicyError, match="byte cap"):
            next(iterator)
    irrelevant = archive_bytes([("irrelevant.bin", b"x" * 10000)])
    with zipfile.ZipFile(BytesIO(irrelevant)) as archive:
        budget = ArchiveBudget(max_bytes=1)
        assert list(iter_xlsx_members(archive, budget=budget)) == []
        assert budget.expanded_bytes == 0


@pytest.mark.parametrize(
    "loader", [iter_xlsx_members, antennal_summaries_from_archive, calcium_datasets_from_archive]
)
def test_all_recursive_readers_enforce_tree_depth(loader):
    tree = archive_bytes([("empty.zip", archive_bytes([]))])
    with zipfile.ZipFile(BytesIO(tree)) as archive, pytest.raises(IntakePolicyError, match="depth"):
        if loader is iter_xlsx_members:
            list(loader(archive, budget=ArchiveBudget(max_depth=0)))
        else:
            loader("dataset", archive, budget=ArchiveBudget(max_depth=0))


def test_directory_entries_count_toward_shared_budget():
    data = archive_bytes([("a/", b""), ("b/", b"")])
    with (
        zipfile.ZipFile(BytesIO(data)) as archive,
        pytest.raises(IntakePolicyError, match="member"),
    ):
        list(iter_xlsx_members(archive, budget=ArchiveBudget(max_members=1)))


@pytest.mark.parametrize("dimension", [None, b"", b'<dimension ref="A1:B2"/>'])
def test_sparse_workbook_actual_coordinates_are_bounded(dimension):
    data = workbook_bytes("F8", dimension=dimension)
    with pytest.raises(IntakePolicyError, match="logical"):
        validate_workbook(data, limits=WorkbookLimits(max_rows=7, max_columns=5, max_cells=100))


@pytest.mark.parametrize("loader", [panels_from_workbook, dataframe_summaries_from_workbook])
def test_both_workbook_readers_reject_before_dense_iteration(monkeypatch, loader):
    import beestack.brain.empirical_parsers.common as common

    monkeypatch.setattr(
        common, "WorkbookLimits", lambda: WorkbookLimits(max_rows=4, max_columns=4, max_cells=16)
    )
    with pytest.raises(IntakePolicyError, match="logical"):
        loader("dataset", "sparse.xlsx", workbook_bytes("F8"))


def test_workbook_package_and_aggregate_sheet_bounds():
    data = workbook_bytes()
    with pytest.raises(IntakePolicyError, match="byte cap"):
        validate_workbook(data, budget=ArchiveBudget(max_bytes=10))
    workbook = Workbook()
    workbook.active["B2"] = 1
    workbook.create_sheet()["B2"] = 2
    stream = BytesIO()
    workbook.save(stream)
    workbook.close()
    with pytest.raises(IntakePolicyError, match="aggregate"):
        validate_workbook(stream.getvalue(), limits=WorkbookLimits(max_total_cells=7))


def hdf5_bytes(build):
    stream = BytesIO()
    with h5py.File(stream, "w") as handle:
        build(handle)
    return stream.getvalue()


@pytest.mark.parametrize("field", ["bee", "padding"])
def test_hdf5_sparse_logical_array_is_rejected_before_array_conversion(monkeypatch, field):
    data = hdf5_bytes(
        lambda handle: handle.create_dataset(field, shape=(2, 2, 2, 1000), chunks=True, dtype="f8")
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("dataset materialized before preflight")

    monkeypatch.setattr(h5py.Dataset, "__array__", forbidden)
    with pytest.raises(IntakePolicyError, match="logical arrays"):
        load_hdf5_mat_payload(data, limits=ArrayLimits(max_bytes=100))


def test_hdf5_cycle_and_variable_length_dtype_are_explicit_rejections():
    def cycle(handle):
        group = handle.create_group("db")
        group["self"] = group

    with pytest.raises(IntakePolicyError, match="cycle"):
        load_hdf5_mat_payload(hdf5_bytes(cycle))
    with pytest.raises(IntakePolicyError, match="fixed-width"):
        load_hdf5_mat_payload(
            hdf5_bytes(
                lambda handle: handle.create_dataset("bee", data=["bad"], dtype=h5py.string_dtype())
            )
        )


@pytest.mark.parametrize("wrapped", [False, True])
def test_real_hdf5_paoli_required_schema_and_aliases(wrapped):
    def build(handle):
        root = handle.create_group("db") if wrapped else handle
        dataset = root.create_dataset("bee", data=np.ones((2, 2, 2, 3)))
        root["alias"] = dataset
        root.create_dataset("fs", data=10.0)

    data = hdf5_bytes(build)
    payload = load_hdf5_mat_payload(data)
    assert (payload["db"] if wrapped else payload)["bee"].shape == (2, 2, 2, 3)
    dataset = calcium_dataset_from_mat_bytes(data)
    assert dataset.traces.shape == (1, 2, 2, 3, 2)
    assert dataset.acquisition_hz == 10.0
    with pytest.raises(IntakePolicyError, match="requires"):
        load_hdf5_mat_payload(hdf5_bytes(lambda handle: handle.create_dataset("padding", data=[1])))


def test_normalization_padding_budget_is_checked_before_stack():
    payload = {"bee": [np.zeros((1, 2, 2, 3), dtype="u1"), np.zeros((4, 2, 2, 3), dtype="u1")]}
    with pytest.raises(IntakePolicyError, match="normalization"):
        validate_paoli_normalization(payload, ArrayLimits(max_bytes=1000))


@pytest.mark.parametrize("compressed", [False, True])
def test_mat_v5_preflight_preserves_real_supported_payload(compressed):
    stream = BytesIO()
    savemat(stream, {"db": {"bee": np.ones((2, 2, 2, 3)), "fs": 10.0}}, do_compression=compressed)
    data = stream.getvalue()
    validate_mat_v5(data)
    assert calcium_dataset_from_mat_bytes(data).traces.shape == (1, 2, 2, 3, 2)
    with pytest.raises(IntakePolicyError):
        validate_mat_v5(data, limits=ArrayLimits(max_bytes=10))


def test_vrml_consumers_read_bounded_prefixes_and_exact_zipinfo(monkeypatch, tmp_path):
    prefix = b"DEF First Transform {} point [0 0 0, 1 1 1] coordIndex [0 1 -1] "
    data = prefix + b" " * 200 + b"DEF Tail Transform {} point [9 9 9]"
    path = tmp_path / "atlas.zip"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("a.wrl", data)
        with pytest.warns(UserWarning, match="Duplicate"):
            archive.writestr("a.wrl", b"DEF Second Transform {} point [2 2 2]")
    monkeypatch.setattr(anatomy, "VRML_PREFIX_BYTES", len(prefix))
    monkeypatch.setattr(structural_wiring, "VRML_PREFIX_BYTES", len(prefix))
    calls = []
    original = zipfile.ZipExtFile.read

    def bounded(self, n=-1):
        calls.append(n)
        assert n >= 0
        return original(self, n)

    monkeypatch.setattr(zipfile.ZipExtFile, "read", bounded)
    inventory = anatomy.atlas_inventory_from_zip(path)
    assert inventory.vrml_vertex_count == 3
    assert structural_wiring._vrml_def_names_from_zip(path) == {"First", "Second"}
    assert calls == [len(prefix)] * 4


@pytest.mark.parametrize("placement", ["root", "files", "zip", "nested"])
@pytest.mark.parametrize("loader", [load_empirical_panels, workbook_dataframe_summaries])
def test_workbook_logical_policy_covers_every_intake_route(
    monkeypatch, tmp_path, placement, loader
):
    import beestack.brain.empirical_parsers.common as common

    monkeypatch.setattr(
        common, "WorkbookLimits", lambda: WorkbookLimits(max_rows=4, max_columns=4, max_cells=16)
    )
    root = tmp_path / "dataset"
    root.mkdir()
    data = workbook_bytes("F8")
    if placement == "root":
        (root / "data.xlsx").write_bytes(data)
    elif placement == "files":
        (root / "files").mkdir()
        (root / "files" / "data.xlsx").write_bytes(data)
    else:
        payload = archive_bytes([("data.xlsx", data)])
        if placement == "nested":
            payload = archive_bytes([("child.zip", payload)])
        (root / "data.zip").write_bytes(payload)
    with pytest.raises(IntakePolicyError, match="logical"):
        loader(tmp_path)


def test_workbook_exact_logical_limit_and_package_member_limit():
    data = workbook_bytes()
    validate_workbook(
        data, limits=WorkbookLimits(max_rows=3, max_columns=2, max_cells=6, max_total_cells=6)
    )
    with pytest.raises(IntakePolicyError, match="logical"):
        validate_workbook(data, limits=WorkbookLimits(max_cells=5))
    with pytest.raises(IntakePolicyError, match="member"):
        validate_workbook(data, limits=WorkbookLimits(max_member_bytes=10))
    with pytest.raises(IntakePolicyError, match="member"):
        validate_workbook(data, budget=ArchiveBudget(max_members=1))


def test_hdf5_graph_depth_compound_dtype_and_required_array_amplification(monkeypatch):
    def deep(handle):
        group = handle.create_group("one")
        group.create_group("two")
        handle.create_dataset("bee", data=np.ones((2, 2, 2, 3)))

    with pytest.raises(IntakePolicyError, match="depth"):
        load_hdf5_mat_payload(hdf5_bytes(deep), limits=ArrayLimits(max_depth=1))
    dtype = np.dtype([("value", "f8")])
    with pytest.raises(IntakePolicyError, match="fixed-width"):
        load_hdf5_mat_payload(
            hdf5_bytes(lambda handle: handle.create_dataset("bee", shape=(2, 2, 2, 3), dtype=dtype))
        )
    data = hdf5_bytes(
        lambda handle: handle.create_dataset("bee", data=np.ones((2, 2, 2, 3), dtype="u1"))
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("scientific array allocated before normalization check")

    monkeypatch.setattr(h5py.Dataset, "__array__", forbidden)
    with pytest.raises(IntakePolicyError, match="normalization"):
        load_hdf5_mat_payload(data, limits=ArrayLimits(max_bytes=300))


def test_legacy_and_tampered_cache_remain_fetch_eligible(tmp_path):
    path = tmp_path / "data"
    path.write_bytes(b"legacy")
    assert empirical_fetch._needs_download(path, force=False, metadata_only=False)
    with response(b"bees", declared=4) as source:
        empirical_fetch._stream_response_to_path(source, path)
    assert completed_download(path)
    path.write_bytes(b"evil")
    assert not completed_download(path)
    assert empirical_fetch._needs_download(path, force=False, metadata_only=False)


def test_redirected_storage_hop_has_no_bearer_and_rejected_hop_never_dispatches(monkeypatch):
    calls = []
    storage = "https://dryad-assetstore-merritt-west.s3.us-west-2.amazonaws.com/a"

    class RecordingHTTPS(urllib.request.HTTPSHandler):
        def https_open(self, request):
            calls.append((request.full_url, request.get_header("Authorization")))
            target = storage if len(calls) == 1 else "https://unlisted.invalid/a"
            return response(
                b"",
                declared=0,
                status=b"302 Found",
                extra=f"Location: {target}\r\n".encode(),
                url=request.full_url,
            )

    original = urllib.request.build_opener
    monkeypatch.setattr(
        urllib.request, "build_opener", lambda *handlers: original(*handlers, RecordingHTTPS())
    )
    monkeypatch.setenv("DRYAD_API_TOKEN", "sentinel")
    with pytest.raises(ValueError):
        empirical_fetch._open_validated_response(
            "https://datadryad.org/api/a", context="test", timeout=1
        )
    assert calls == [("https://datadryad.org/api/a", "Bearer sentinel"), (storage, None)]


def test_real_redirect_loop_terminates_and_closes_responses(monkeypatch):
    sources = []

    class LoopHTTPS(urllib.request.HTTPSHandler):
        def https_open(self, request):
            source = response(
                b"",
                declared=0,
                status=b"302 Found",
                extra=b"Location: /a\r\n",
                url=request.full_url,
            )
            sources.append(source)
            return source

    original = urllib.request.build_opener
    monkeypatch.setattr(
        urllib.request, "build_opener", lambda *handlers: original(*handlers, LoopHTTPS())
    )
    with pytest.raises(empirical_fetch.urllib.error.HTTPError):
        empirical_fetch._open_validated_response(
            "https://figshare.com/a", context="test", timeout=1
        )
    assert 1 < len(sources) < 12
    assert all(source.isclosed() for source in sources)


@pytest.mark.parametrize("kind", ["antennal", "calcium"])
def test_other_archive_readers_share_expanded_byte_budget_across_siblings(kind):
    if kind == "antennal":
        payload = (
            b"Bee,Plume,Frame,Odor_detector,LeftTheta,RightTheta\n1,1,0,1,0,10\n1,1,1,1,10,20\n"
        )
        inner = archive_bytes([("movement.csv", payload)])
        loader = antennal_summaries_from_archive
    else:
        stream = BytesIO()
        savemat(stream, {"db": {"bee": np.ones((2, 2, 2, 3)), "fs": 10.0}})
        payload = stream.getvalue()
        inner = archive_bytes([("bee.mat", payload)])
        loader = calcium_datasets_from_archive
    tree = archive_bytes([("one.zip", inner), ("two.zip", inner)])
    one_branch = len(inner) + len(payload)
    with (
        zipfile.ZipFile(BytesIO(tree)) as archive,
        pytest.raises(IntakePolicyError, match="byte cap"),
    ):
        loader("dataset", archive, budget=ArchiveBudget(max_bytes=one_branch))
