"""Szyszka et al. MDPI supplementary Table S1 parser."""

from __future__ import annotations

import re
import zipfile
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from ...security import assert_safe_zip_member, validate_zip_archive_bounds
from ..empirical_data import SzyszkaGrangerSupplementSummary, SzyszkaTemplateTestRow

DATASET_ID = "szyszka-2023-granger-al-network"
ODOR_LABELS = ("1HEX", "3HEX", "1NON", "ISOA", "ACPH", "BZDA")
_TRIPLET_PATTERN = re.compile(
    r"(?P<original_p>\d+(?:\.\d+)?(?:e[+-]?\d+)?)\s+"
    r"(?P<fdr_p>\d+(?:\.\d+)?(?:e[+-]?\d+)?)\s+"
    r"(?P<w>\d+)"
)


def parse_table_s1_text(text: str) -> tuple[SzyszkaTemplateTestRow, ...]:
    """Parse Wilcoxon Table S1 numeric triplets from supplementary PDF text."""

    marker = "Supplementary Table S1"
    if marker not in text:
        return ()
    section = text.split(marker, 1)[1]
    rows: list[SzyszkaTemplateTestRow] = []
    for odor in ODOR_LABELS:
        odor_match = re.search(
            rf"\b{re.escape(odor)}\b\s*(?P<body>.*?)(?=\b(?:{'|'.join(ODOR_LABELS)})\b|$)",
            section,
            re.S,
        )
        if not odor_match:
            continue
        triplets = _TRIPLET_PATTERN.findall(odor_match.group("body"))
        for condition_index, (original_p, fdr_p, w_text) in enumerate(triplets):
            rows.append(
                SzyszkaTemplateTestRow(
                    odor=odor,
                    condition_index=condition_index,
                    original_p=float(original_p),
                    fdr_p=float(fdr_p),
                    signed_rank_w=int(w_text),
                )
            )
    return tuple(rows)


def _pdf_text_from_supplement_path(path: Path) -> str:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            validate_zip_archive_bounds(archive)
            pdf_names = [
                info.filename
                for info in archive.infolist()
                if not info.is_dir() and info.filename.lower().endswith(".pdf")
            ]
            if not pdf_names:
                return ""
            assert_safe_zip_member(pdf_names[0])
            payload = archive.read(pdf_names[0])
        reader = PdfReader(BytesIO(payload))
    else:
        reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def load_szyszka_granger_supplement(source_dir: Path) -> SzyszkaGrangerSupplementSummary | None:
    """Load Szyszka MDPI supplementary Table S1 when the publisher zip is local."""

    dataset_dir = source_dir / DATASET_ID / "supplementary"
    if not dataset_dir.exists():
        return None
    candidates = sorted(dataset_dir.glob("*.zip")) + sorted(dataset_dir.glob("*.pdf"))
    if not candidates:
        return None
    source_path = candidates[0]
    text = _pdf_text_from_supplement_path(source_path)
    rows = parse_table_s1_text(text)
    if not rows:
        return None
    odor_labels = tuple(dict.fromkeys(row.odor for row in rows))
    return SzyszkaGrangerSupplementSummary(
        dataset_id=DATASET_ID,
        table_s1_row_count=len(rows),
        odor_labels=odor_labels,
        rows=rows,
        var_connectivity_available=False,
        source_files=(str(source_path),),
    )
