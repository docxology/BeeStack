"""Paoli-style MATLAB calcium dataset loaders."""

from __future__ import annotations

import math
import struct
import zipfile
import zlib
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
from scipy.io import loadmat

from ...security import (
    ArchiveBudget,
    IntakePolicyError,
    assert_safe_zip_member,
    validate_zip_archive_bounds,
)
from .. import empirical_data
from ..empirical_data import EmpiricalCalciumDataset, parse_paoli_matlab_payload
from .common import dataset_id_from_path


def _is_macos_metadata(member_name: str) -> bool:
    parts = Path(member_name).parts
    return any(part == "__MACOSX" or part.startswith("._") for part in parts)


def load_calcium_datasets(source_dir: Path) -> tuple[EmpiricalCalciumDataset, ...]:
    datasets: list[EmpiricalCalciumDataset] = []
    for zip_path in sorted(source_dir.glob("*/*.zip")):
        dataset_id = zip_path.parent.name
        with zipfile.ZipFile(zip_path) as archive:
            validate_zip_archive_bounds(archive)
            datasets.extend(calcium_datasets_from_archive(dataset_id, archive))
    for mat_path in sorted(source_dir.glob("*/files/**/*.mat")):
        dataset = calcium_dataset_from_mat_bytes(mat_path.read_bytes())
        if dataset is not None:
            datasets.append(dataset)
    for zip_path in sorted(source_dir.glob("*/files/**/*.mat.zip")):
        with zipfile.ZipFile(zip_path) as archive:
            validate_zip_archive_bounds(archive)
            datasets.extend(
                calcium_datasets_from_archive(
                    dataset_id_from_path(source_dir, zip_path), archive, prefix=f"{zip_path.name}/"
                )
            )
    return tuple(datasets)


def calcium_datasets_from_archive(
    dataset_id: str,
    archive: zipfile.ZipFile,
    prefix: str = "",
    *,
    budget: ArchiveBudget | None = None,
    depth: int = 0,
) -> list[EmpiricalCalciumDataset]:
    datasets: list[EmpiricalCalciumDataset] = []
    budget = budget if budget is not None else ArchiveBudget()
    budget.enter(archive, depth)
    for info in archive.infolist():
        if info.is_dir():
            continue
        assert_safe_zip_member(info.filename)
        if _is_macos_metadata(info.filename):
            continue
        member_name = f"{prefix}{info.filename}"
        lowered = info.filename.lower()
        if lowered.endswith(".mat"):
            budget.consume(info)
            dataset = calcium_dataset_from_mat_bytes(archive.read(info), member_name)
            if dataset is not None:
                datasets.append(dataset)
        elif lowered.endswith(".zip"):
            budget.consume(info)
            with zipfile.ZipFile(BytesIO(archive.read(info))) as nested:
                datasets.extend(
                    calcium_datasets_from_archive(
                        dataset_id, nested, prefix=f"{member_name}/", budget=budget, depth=depth + 1
                    )
                )
    return datasets


def _is_hdf5_container(data: bytes) -> bool:
    # HDF5 permits a signature at zero or 512 * 2**n, for any user-block size.
    # Probe only those offsets present in this byte buffer, never scan its contents.
    offset = 0
    while offset + 8 <= len(data):
        if data[offset : offset + 8] == b"\x89HDF\r\n\x1a\n":
            return True
        offset = 512 if offset == 0 else offset * 2
    return False


def calcium_dataset_from_mat_bytes(
    data: bytes, source_name: str = "matlab_payload"
) -> EmpiricalCalciumDataset | None:
    if _is_hdf5_container(data):
        payload = load_hdf5_mat_payload(data)
    else:
        validate_mat_v5(data)
        payload = loadmat(
            BytesIO(data),
            squeeze_me=False,
            struct_as_record=False,
            variable_names=("db", "bee", "fs", "odors", "glomeruli"),
        )
        # Unwrap only the scalar MATLAB struct, never scientific tensor axes.
        # squeeze_me=True loses singleton odor/trial/glomerulus dimensions.
        db = payload.get("db")
        if isinstance(db, np.ndarray) and db.dtype == object and db.size == 1:
            payload["db"] = db.item()
    validate_paoli_normalization(payload)
    dataset = parse_paoli_matlab_payload(payload)
    return EmpiricalCalciumDataset(
        dataset_id=dataset.dataset_id,
        traces=dataset.traces,
        acquisition_hz=dataset.acquisition_hz,
        odor_labels=dataset.odor_labels,
        glomerulus_labels=dataset.glomerulus_labels,
        source_variables=tuple((*dataset.source_variables, source_name)),
    )


def validate_paoli_normalization(
    payload: dict[str, Any], limits: empirical_data.ArrayLimits | None = None
) -> None:
    """Account for float64 conversion, padding and the final stacked copy."""
    limits = limits or empirical_data.ArrayLimits()
    db = payload.get("db", payload)
    bee = db.get("bee") if isinstance(db, dict) else getattr(db, "bee", None)
    if bee is None:
        raise IntakePolicyError("Paoli payload requires db.bee")
    if isinstance(bee, np.ndarray) and bee.dtype == object:
        arrays = list(bee.flat)
    elif isinstance(bee, (list, tuple)):
        arrays = list(bee)
    elif isinstance(bee, np.ndarray) and bee.ndim == 5:
        arrays = [bee[index] for index in range(bee.shape[0])]
    else:
        arrays = [bee]
    if not arrays or len(arrays) > limits.max_nodes:
        raise IntakePolicyError("invalid Paoli bee count")
    shapes = [np.shape(array) for array in arrays]
    if any(len(shape) != 4 or min(shape) <= 0 for shape in shapes):
        raise IntakePolicyError("Paoli bee arrays require four nonempty axes")
    if any(shape[1:] != shapes[0][1:] for shape in shapes):
        raise IntakePolicyError("Paoli bee odor/trial/time axes must agree")
    normalized = len(shapes) * max(shape[0] for shape in shapes) * math.prod(shapes[0][1:]) * 8
    original = sum(math.prod(shape) * 8 for shape in shapes)
    if original + 2 * normalized > limits.max_bytes:
        raise IntakePolicyError("Paoli float normalization exceeds byte cap")


def load_hdf5_mat_payload(
    data: bytes, *, limits: empirical_data.ArrayLimits | None = None
) -> dict[str, Any]:
    import h5py

    limits = limits or empirical_data.ArrayLimits()
    with h5py.File(BytesIO(data), "r") as handle:
        active: set[int] = set()
        visited: set[int] = set()
        charged = 0

        def preflight(value, depth=0):
            nonlocal charged
            identity = h5py.h5o.get_info(value.id).addr
            if identity in active:
                raise IntakePolicyError("HDF5 hard-link/reference cycle")
            if depth > limits.max_depth:
                raise IntakePolicyError("HDF5 graph exceeds depth/node cap")
            if identity in visited:
                return
            if len(visited) >= limits.max_nodes:
                raise IntakePolicyError("HDF5 graph exceeds depth/node cap")
            visited.add(identity)
            active.add(identity)
            if isinstance(value, h5py.Group):
                for key in value:
                    link = value.get(key, getlink=True)
                    if not isinstance(link, h5py.HardLink):
                        raise IntakePolicyError("HDF5 external/soft links are unsupported")
                    preflight(value[key], depth + 1)
            else:
                storage = value.id.get_create_plist()
                if storage.get_external_count():
                    raise IntakePolicyError("HDF5 external raw storage is unsupported")
                if storage.get_layout() == h5py.h5d.VIRTUAL:
                    raise IntakePolicyError("HDF5 virtual datasets are unsupported")
                dtype = value.dtype
                if dtype.hasobject or dtype.fields is not None or dtype.kind not in "biufcSU":
                    raise IntakePolicyError("HDF5 requires fixed-width numeric/string datasets")
                charged += math.prod(value.shape) * max(dtype.itemsize, 8)
                if charged > limits.max_bytes:
                    raise IntakePolicyError("HDF5 logical arrays exceed byte cap")
            active.remove(identity)

        preflight(handle)
        root = handle.get("db", handle)
        if not isinstance(root, h5py.Group) or "bee" not in root:
            raise IntakePolicyError("HDF5 Paoli schema requires db.bee")
        bee = root["bee"]
        if isinstance(bee, h5py.Group):
            raise IntakePolicyError("HDF5 Paoli db.bee must be a numeric 4D/5D dataset")
        shape = bee.shape
        if len(shape) not in (4, 5) or not shape or min(shape) <= 0:
            raise IntakePolicyError("HDF5 Paoli bee arrays require four/five nonempty axes")
        selected = {
            key: root[key]
            for key in ("bee", "fs", "odors", "glomeruli")
            if key in root and isinstance(root[key], h5py.Dataset)
        }
        # Labels become boxed Python strings; fs also receives a float64 copy.
        materialized = sum(
            math.prod(value.shape)
            * (
                value.dtype.itemsize * 4 + 128
                if key in {"odors", "glomeruli"}
                else max(value.dtype.itemsize, 8) * (2 if key == "fs" else 1)
            )
            for key, value in selected.items()
        )
        if materialized + 3 * math.prod(shape) * 8 > limits.max_bytes:
            raise IntakePolicyError("HDF5 Paoli float normalization exceeds byte cap")
        payload = {key: np.asarray(value) for key, value in selected.items()}
        validate_paoli_normalization(payload, limits)
        return {"db": payload} if "db" in handle else payload


def validate_mat_v5(data: bytes, *, limits: empirical_data.ArrayLimits | None = None) -> None:
    """Bound compressed streams and every nested matrix shape before SciPy allocation."""
    limits = limits or empirical_data.ArrayLimits()
    if len(data) < 128 or data[126:128] not in (b"IM", b"MI"):
        raise IntakePolicyError("only MATLAB v5 or HDF5 calcium containers are supported")
    endian = "<" if data[126:128] == b"IM" else ">"
    charged = nodes = 0

    def scan(block, depth=0):
        nonlocal charged, nodes
        if depth > limits.max_depth:
            raise IntakePolicyError("MATLAB matrix graph exceeds depth cap")
        offset = 0
        while offset < len(block):
            if len(block) - offset < 8:
                raise IntakePolicyError("truncated MATLAB tag")
            kind, size = struct.unpack_from(endian + "II", block, offset)
            small = kind >> 16
            if small:
                if small > 4:
                    raise IntakePolicyError("invalid small MATLAB tag")
                offset += 8
                continue
            start, stop = offset + 8, offset + 8 + size
            if stop > len(block):
                raise IntakePolicyError("truncated MATLAB element")
            payload = memoryview(block)[start:stop]
            nodes += 1
            if nodes > limits.max_nodes:
                raise IntakePolicyError("MATLAB element count exceeds cap")
            if kind == 15:  # miCOMPRESSED (not padded by scipy/MATLAB writers)
                decoder = zlib.decompressobj()
                expanded = decoder.decompress(payload, limits.max_bytes - charged + 1)
                charged += len(expanded)
                if charged > limits.max_bytes or not decoder.eof or decoder.unused_data:
                    raise IntakePolicyError(
                        "MATLAB compressed data exceeds byte cap or is incomplete"
                    )
                scan(expanded, depth + 1)
            elif kind == 14:  # miMATRIX: flags, dimensions, name, then values/children
                if len(payload) < 24:
                    raise IntakePolicyError("invalid MATLAB matrix header")
                dims_kind, dims_size = struct.unpack_from(endian + "II", payload, 16)
                if (
                    dims_kind != 5
                    or dims_size % 4
                    or not 8 <= dims_size <= 128
                    or 24 + dims_size > len(payload)
                ):
                    raise IntakePolicyError("invalid MATLAB dimensions")
                dims = struct.unpack_from(endian + "i" * (dims_size // 4), payload, 24)
                if any(dimension < 0 for dimension in dims):
                    raise IntakePolicyError("negative MATLAB dimension")
                charged += math.prod(dims) * 8 * 4
                if charged > limits.max_bytes:
                    raise IntakePolicyError("MATLAB logical arrays exceed byte cap")
                scan(payload, depth + 1)
            offset = stop if kind == 15 else start + ((size + 7) // 8) * 8

    scan(memoryview(data)[128:])
