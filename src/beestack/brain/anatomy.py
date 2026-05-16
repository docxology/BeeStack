"""Honeybee Standard Brain anatomy download records and parsers."""

from __future__ import annotations

import re
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from PIL import Image

from .datasets import BeeBrainAtlasAsset


@dataclass(frozen=True)
class AtlasDownloadRecord:
    """Local status for one curated Honeybee Standard Brain atlas asset."""

    dataset_id: str
    asset_id: str
    url: str
    local_path: str
    size_bytes: int
    downloaded: bool
    skipped_existing: bool
    sha256: str | None = None
    error: str | None = None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AtlasInventory:
    """Parsed inventory and lightweight geometry metadata for one atlas archive."""

    asset_id: str
    local_path: str
    file_count: int
    suffix_counts: dict[str, int]
    total_uncompressed_bytes: int
    representative_files: tuple[str, ...]
    tiff_count: int
    vrml_count: int
    image_shape: tuple[int, int] | None
    vrml_vertex_count: int
    vrml_face_count: int
    vrml_bounds_min: tuple[float, float, float] | None = None
    vrml_bounds_max: tuple[float, float, float] | None = None
    vrml_centroid: tuple[float, float, float] | None = None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class NeuropilAbbreviation:
    """One Honeybee Standard Brain neuropil abbreviation entry."""

    abbreviation: str
    label: str
    side: str
    region_class: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class BeeBrainAnatomySummary:
    """Compact end-to-end summary of downloaded anatomy assets."""

    dataset_id: str
    asset_count: int
    downloaded_asset_count: int
    inventory_count: int
    neuropil_count: int
    bilateral_pair_count: int
    vrml_file_count: int
    tiff_file_count: int
    total_uncompressed_bytes: int
    major_regions: dict[str, int]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class _TableTextParser(HTMLParser):
    """Small permissive parser for FU Berlin's abbreviation table."""

    def __init__(self) -> None:
        super().__init__()
        self._cell_parts: list[str] = []
        self._current_row: list[str] = []
        self._in_cell = False
        self.rows: list[tuple[str, ...]] = []
        self.list_items: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"td", "th", "li"}:
            self._in_cell = True
            self._cell_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered in {"td", "th"} and self._in_cell:
            self._current_row.append(_clean_text(" ".join(self._cell_parts)))
            self._cell_parts = []
            self._in_cell = False
        elif lowered == "li" and self._in_cell:
            self.list_items.append(_clean_text(" ".join(self._cell_parts)))
            self._cell_parts = []
            self._in_cell = False
        elif lowered == "tr":
            row = tuple(cell for cell in self._current_row if cell)
            if row:
                self.rows.append(row)
            self._current_row = []


def atlas_download_record_from_asset(
    dataset_id: str,
    asset: BeeBrainAtlasAsset,
    local_path: Path,
    *,
    skipped_existing: bool = False,
    error: str | None = None,
    sha256: str | None = None,
) -> AtlasDownloadRecord:
    """Create a typed local-download record for an atlas asset."""

    downloaded = local_path.exists() and local_path.stat().st_size > 0
    return AtlasDownloadRecord(
        dataset_id=dataset_id,
        asset_id=asset.asset_id,
        url=asset.url,
        local_path=str(local_path),
        size_bytes=local_path.stat().st_size if downloaded else 0,
        downloaded=downloaded,
        skipped_existing=skipped_existing,
        sha256=sha256,
        error=error,
    )


def atlas_inventory_from_zip(path: Path, asset_id: str | None = None) -> AtlasInventory:
    """Inspect an atlas ZIP without extracting it to project source."""

    suffix_counts: Counter[str] = Counter()
    total_uncompressed = 0
    files: list[str] = []
    image_shape: tuple[int, int] | None = None
    vertex_count = 0
    face_count = 0
    bounds_min: tuple[float, float, float] | None = None
    bounds_max: tuple[float, float, float] | None = None
    centroid_sum = _zero3()
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            files.append(info.filename)
            total_uncompressed += int(info.file_size)
            suffix = Path(info.filename).suffix.lower() or "<none>"
            suffix_counts[suffix] += 1
            lowered = info.filename.lower()
            if image_shape is None and lowered.endswith((".tif", ".tiff", ".jpg", ".jpeg", ".png")):
                image_shape = _image_shape_from_member(archive, info.filename)
            if lowered.endswith((".wrl", ".vrml")):
                geometry = _vrml_geometry(archive.read(info.filename))
                vertices = int(geometry["vertex_count"])
                faces = int(geometry["face_count"])
                vertex_count += vertices
                face_count += faces
                centroid = geometry["centroid"]
                if centroid is not None and vertices > 0:
                    centroid_sum = (
                        centroid_sum[0] + centroid[0] * vertices,
                        centroid_sum[1] + centroid[1] * vertices,
                        centroid_sum[2] + centroid[2] * vertices,
                    )
                bounds_min = _min3(bounds_min, geometry["bounds_min"])
                bounds_max = _max3(bounds_max, geometry["bounds_max"])
    tiff_count = suffix_counts[".tif"] + suffix_counts[".tiff"]
    vrml_count = suffix_counts[".wrl"] + suffix_counts[".vrml"]
    return AtlasInventory(
        asset_id=asset_id or _asset_id_from_path(path),
        local_path=str(path),
        file_count=len(files),
        suffix_counts=dict(sorted(suffix_counts.items())),
        total_uncompressed_bytes=total_uncompressed,
        representative_files=tuple(files[:10]),
        tiff_count=tiff_count,
        vrml_count=vrml_count,
        image_shape=image_shape,
        vrml_vertex_count=vertex_count,
        vrml_face_count=face_count,
        vrml_bounds_min=bounds_min,
        vrml_bounds_max=bounds_max,
        vrml_centroid=_scale3(centroid_sum, 1.0 / vertex_count) if vertex_count > 0 else None,
    )


def atlas_inventories_from_directory(directory: Path) -> tuple[AtlasInventory, ...]:
    """Return inventories for every atlas ZIP present in a dataset directory."""

    inventories: list[AtlasInventory] = []
    for path in sorted(directory.glob("*.zip")):
        if path.exists() and path.stat().st_size > 0:
            inventories.append(atlas_inventory_from_zip(path))
    return tuple(inventories)


def neuropil_abbreviations_from_html(html: str) -> tuple[NeuropilAbbreviation, ...]:
    """Parse FU Berlin neuropil abbreviation HTML into typed entries."""

    parser = _TableTextParser()
    parser.feed(html)
    entries: list[NeuropilAbbreviation] = []
    seen: set[str] = set()
    rows = list(parser.rows)
    rows.extend(
        tuple(part.strip() for part in item.split("=", maxsplit=1))
        for item in parser.list_items
        if "=" in item
    )
    for row in rows:
        if len(row) < 2:
            continue
        abbreviation, label = _choose_abbreviation_label(row)
        if not abbreviation or not label or abbreviation.lower() in {"abbreviation", "abbr"}:
            continue
        if not _looks_like_abbreviation(abbreviation):
            continue
        key = abbreviation.lower()
        if key in seen:
            continue
        seen.add(key)
        entries.append(
            NeuropilAbbreviation(
                abbreviation=abbreviation,
                label=label,
                side=_side_from_abbreviation(abbreviation),
                region_class=_region_class(abbreviation, label),
            )
        )
    return tuple(entries)


def load_neuropil_abbreviations(path: Path) -> tuple[NeuropilAbbreviation, ...]:
    """Load neuropil abbreviations from a downloaded FU Berlin HTML file."""

    if not path.exists() or path.stat().st_size == 0:
        return ()
    return neuropil_abbreviations_from_html(path.read_text(encoding="utf-8", errors="replace"))


def summarize_anatomy(
    records: tuple[AtlasDownloadRecord, ...],
    inventories: tuple[AtlasInventory, ...],
    abbreviations: tuple[NeuropilAbbreviation, ...],
    dataset_id: str = "virtual-honeybee-standard-brain",
) -> BeeBrainAnatomySummary:
    """Aggregate local Honeybee Standard Brain anatomy evidence."""

    sides_by_region: dict[str, set[str]] = {}
    for entry in abbreviations:
        base = _strip_side(entry.abbreviation)
        if entry.side in {"left", "right"} and base:
            sides_by_region.setdefault(base, set()).add(entry.side)
    region_counts = Counter(entry.region_class for entry in abbreviations)
    return BeeBrainAnatomySummary(
        dataset_id=dataset_id,
        asset_count=len(records),
        downloaded_asset_count=sum(1 for record in records if record.downloaded),
        inventory_count=len(inventories),
        neuropil_count=len(abbreviations),
        bilateral_pair_count=sum(
            1 for sides in sides_by_region.values() if {"left", "right"} <= sides
        ),
        vrml_file_count=sum(inventory.vrml_count for inventory in inventories),
        tiff_file_count=sum(inventory.tiff_count for inventory in inventories),
        total_uncompressed_bytes=sum(
            inventory.total_uncompressed_bytes for inventory in inventories
        ),
        major_regions=dict(sorted(region_counts.items())),
    )


def atlas_download_records_from_dicts(
    rows: tuple[dict[str, Any], ...],
) -> tuple[AtlasDownloadRecord, ...]:
    """Deserialize atlas download records from JSON-compatible dictionaries."""

    records: list[AtlasDownloadRecord] = []
    for row in rows:
        records.append(
            AtlasDownloadRecord(
                dataset_id=str(row.get("dataset_id", "")),
                asset_id=str(row.get("asset_id", "")),
                url=str(row.get("url", "")),
                local_path=str(row.get("local_path", "")),
                size_bytes=int(row.get("size_bytes") or 0),
                downloaded=bool(row.get("downloaded")),
                skipped_existing=bool(row.get("skipped_existing")),
                sha256=str(row["sha256"]) if row.get("sha256") else None,
                error=str(row["error"]) if row.get("error") else None,
            )
        )
    return tuple(records)


def _asset_id_from_path(path: Path) -> str:
    stem = path.stem.lower().replace("_", "-")
    return f"hsb-{stem}"


def _image_shape_from_member(archive: zipfile.ZipFile, name: str) -> tuple[int, int] | None:
    try:
        with archive.open(name) as raw, Image.open(raw) as image:
            width, height = image.size
            return int(height), int(width)
    except Exception:
        return None


def _vrml_geometry(data: bytes) -> dict[str, Any]:
    text = data[:5_000_000].decode("utf-8", "ignore")
    point_sections = re.findall(r"point\s*\[([^\]]*)\]", text, flags=re.IGNORECASE | re.DOTALL)
    vertex_count = 0
    bounds_min: tuple[float, float, float] | None = None
    bounds_max: tuple[float, float, float] | None = None
    centroid_sum = _zero3()
    for section in point_sections:
        values = [float(value) for value in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", section)]
        for idx in range(0, len(values) - 2, 3):
            point = (values[idx], values[idx + 1], values[idx + 2])
            vertex_count += 1
            bounds_min = _min3(bounds_min, point)
            bounds_max = _max3(bounds_max, point)
            centroid_sum = (
                centroid_sum[0] + point[0],
                centroid_sum[1] + point[1],
                centroid_sum[2] + point[2],
            )
    coord_sections = re.findall(r"coordIndex\s*\[([^\]]*)\]", text, flags=re.IGNORECASE | re.DOTALL)
    face_count = sum(section.count("-1") for section in coord_sections)
    return {
        "vertex_count": vertex_count,
        "face_count": face_count,
        "bounds_min": bounds_min,
        "bounds_max": bounds_max,
        "centroid": _scale3(centroid_sum, 1.0 / vertex_count) if vertex_count > 0 else None,
    }


def _zero3() -> tuple[float, float, float]:
    return (0.0, 0.0, 0.0)


def _min3(
    left: tuple[float, float, float] | None,
    right: tuple[float, float, float] | None,
) -> tuple[float, float, float] | None:
    if left is None:
        return right
    if right is None:
        return left
    return (min(left[0], right[0]), min(left[1], right[1]), min(left[2], right[2]))


def _max3(
    left: tuple[float, float, float] | None,
    right: tuple[float, float, float] | None,
) -> tuple[float, float, float] | None:
    if left is None:
        return right
    if right is None:
        return left
    return (max(left[0], right[0]), max(left[1], right[1]), max(left[2], right[2]))


def _scale3(vector: tuple[float, float, float], scalar: float) -> tuple[float, float, float]:
    return (vector[0] * scalar, vector[1] * scalar, vector[2] * scalar)


def _choose_abbreviation_label(row: tuple[str, ...]) -> tuple[str, str]:
    first, second = row[0], row[1]
    if _looks_like_abbreviation(first):
        return first, second
    if _looks_like_abbreviation(second):
        return second, first
    return first, second


def _looks_like_abbreviation(text: str) -> bool:
    token = text.strip()
    return bool(token) and len(token) <= 18 and bool(re.search(r"[A-Za-z]", token))


def _side_from_abbreviation(abbreviation: str) -> str:
    lowered = abbreviation.lower()
    if lowered.startswith(("l-", "left ")):
        return "left"
    if lowered.startswith(("r-", "right ")):
        return "right"
    return "midline"


def _strip_side(abbreviation: str) -> str:
    lowered = abbreviation.lower()
    if lowered.startswith(("l-", "r-")):
        return abbreviation[2:]
    return abbreviation


def _region_class(abbreviation: str, label: str) -> str:
    text = f"{abbreviation} {label}".lower()
    if any(token in text for token in ("antennal lobe", " al", " glomer")):
        return "antennal_lobe"
    if any(
        token in text
        for token in (
            "mushroom",
            "calyx",
            "pedunc",
            "alpha lobe",
            "vertical lobe",
            "basal ring",
            "collar",
            " lip",
            "vmb",
            "medbr",
            "latbr",
        )
    ):
        return "mushroom_body"
    if any(
        token in text
        for token in (
            "central complex",
            "central body",
            "ellipsoid",
            "fan-shaped",
            "protocerebral bridge",
        )
    ):
        return "central_complex"
    if any(token in text for token in ("lobula", "medulla", "lamina", "optic")):
        return "optic_lobe"
    if any(token in text for token in ("tract", "commissure", "nerve")):
        return "tract"
    return "neuropil"


def _clean_text(text: str) -> str:
    return " ".join(text.replace("\xa0", " ").split())
