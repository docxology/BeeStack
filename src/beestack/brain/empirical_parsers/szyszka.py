"""Szyszka et al. MDPI supplementary Table S1 parser."""

from __future__ import annotations

import math
import re
import zipfile
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from ...security import assert_safe_zip_member, validate_zip_archive_bounds
from ..empirical_data import SzyszkaGrangerSupplementSummary, SzyszkaTemplateTestRow

DATASET_ID = "szyszka-2023-granger-al-network"
ODOR_LABELS = ("1HEX", "3HEX", "1NON", "ISOA", "ACPH", "BZDA")
_PROBABILITY_PATTERN = re.compile(r"[+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")
_TABLE_END_PATTERN = re.compile(
    r"^(?:Supplementary Figure\b|Figure\s+S?\d+\b|"
    r"Page\s+\d+(?:\s+of\s+\d+)?\s*$|\d+\s+of\s+\d+\s*$|"
    r"Insects\s+\d{4},.*\d+\s+of\s+\d+\s*$)",
    re.I,
)


def _table_s1_section(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        # Numeric rows (including malformed ones) must reach strict validation.
        # A full prose sentence is not another statistical triplet.
        prose = (
            re.fullmatch(r"[A-Za-z][A-Za-z\s,;:'’()\-]*[.!?]", stripped) is not None
            and len(stripped.split()) >= 4
        )
        if _TABLE_END_PATTERN.match(stripped) or (lines and prose):
            break
        lines.append(line)
    return "\n".join(lines)


def parse_table_s1_text(text: str) -> tuple[SzyszkaTemplateTestRow, ...]:
    """Parse complete numeric odor blocks; reject missing or invalid statistics."""

    marker = re.search(r"\bSupplementary Table S1\b", text)
    if marker is None:
        return ()
    section = re.split(r"\bSupplementary Table S\d+\b", text[marker.end() :], maxsplit=1)[0]
    # Stop at recognizable non-table material, not at an invalid numeric row.
    # Initial table-title prose precedes the first odor and is not table data.
    first_odor = re.search(rf"\b(?:{'|'.join(ODOR_LABELS)})\b", section)
    if first_odor is None:
        return ()
    section = _table_s1_section(section[first_odor.start() :])
    rows: list[SzyszkaTemplateTestRow] = []
    for odor in ODOR_LABELS:
        condition_index = 0
        for odor_match in re.finditer(
            rf"\b{re.escape(odor)}\b\s*(?P<body>.*?)(?=\b(?:{'|'.join(ODOR_LABELS)})\b|$)",
            section,
            re.S,
        ):
            tokens = odor_match.group("body").split()
            if not tokens or len(tokens) % 3:
                raise ValueError(f"incomplete Table S1 statistical triplets for {odor}")
            for offset in range(0, len(tokens), 3):
                original_p, fdr_p, w_text = tokens[offset : offset + 3]
                if (
                    _PROBABILITY_PATTERN.fullmatch(original_p) is None
                    or _PROBABILITY_PATTERN.fullmatch(fdr_p) is None
                    or _PROBABILITY_PATTERN.fullmatch(w_text) is None
                ):
                    raise ValueError(f"invalid Table S1 statistical triplet for {odor}")
                original, corrected = float(original_p), float(fdr_p)
                signed_rank_w = float(w_text)
                if not math.isfinite(signed_rank_w) or signed_rank_w < 0.0:
                    raise ValueError(
                        f"Table S1 signed rank W must be finite and nonnegative for {odor}"
                    )
                if not 0.0 <= original <= 1.0 or not 0.0 <= corrected <= 1.0:
                    raise ValueError(f"Table S1 probabilities must be in [0, 1] for {odor}")
                rows.append(
                    SzyszkaTemplateTestRow(
                        odor=odor,
                        condition_index=condition_index,
                        original_p=original,
                        fdr_p=corrected,
                        signed_rank_w=signed_rank_w,
                    )
                )
                condition_index += 1
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
