"""Paoli-style MATLAB calcium dataset loaders."""

from __future__ import annotations

import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
from scipy.io import loadmat

from ...security import assert_safe_zip_member, validate_zip_archive_bounds
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
) -> list[EmpiricalCalciumDataset]:
    datasets: list[EmpiricalCalciumDataset] = []
    for info in archive.infolist():
        if info.is_dir():
            continue
        assert_safe_zip_member(info.filename)
        if _is_macos_metadata(info.filename):
            continue
        member_name = f"{prefix}{info.filename}"
        lowered = info.filename.lower()
        if lowered.endswith(".mat"):
            dataset = calcium_dataset_from_mat_bytes(archive.read(info), member_name)
            if dataset is not None:
                datasets.append(dataset)
        elif lowered.endswith(".zip"):
            with zipfile.ZipFile(BytesIO(archive.read(info))) as nested:
                validate_zip_archive_bounds(nested)
                datasets.extend(
                    calcium_datasets_from_archive(dataset_id, nested, prefix=f"{member_name}/")
                )
    return datasets


def calcium_dataset_from_mat_bytes(
    data: bytes, source_name: str = "matlab_payload"
) -> EmpiricalCalciumDataset | None:
    try:
        payload = loadmat(BytesIO(data), squeeze_me=True, struct_as_record=False)
    except (NotImplementedError, ValueError):
        try:
            payload = load_hdf5_mat_payload(data)
        except (ValueError, OSError):
            return None
    except Exception:
        return None
    try:
        dataset = parse_paoli_matlab_payload(payload)
    except (TypeError, ValueError, KeyError):
        return None
    return EmpiricalCalciumDataset(
        dataset_id=dataset.dataset_id,
        traces=dataset.traces,
        acquisition_hz=dataset.acquisition_hz,
        odor_labels=dataset.odor_labels,
        glomerulus_labels=dataset.glomerulus_labels,
        source_variables=tuple((*dataset.source_variables, source_name)),
    )


def load_hdf5_mat_payload(data: bytes) -> dict[str, Any]:
    try:
        import h5py
    except ImportError as exc:
        raise ValueError("HDF5 MATLAB file requires h5py") from exc
    with h5py.File(BytesIO(data), "r") as handle:
        return {key: hdf5_to_plain(value) for key, value in handle.items()}


def hdf5_to_plain(value: Any) -> Any:
    if hasattr(value, "items"):
        return {key: hdf5_to_plain(child) for key, child in value.items()}
    return np.asarray(value)
