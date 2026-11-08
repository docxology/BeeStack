"""Nouvian workbook sheet heuristics."""

from __future__ import annotations

import re
from typing import Any

from .common import join_label, normalize_header, numeric, text


def nouvian_rows_from_sheet(
    workbook_name: str,
    sheet_name: str,
    table: list[tuple[Any, ...]],
) -> list[dict[str, Any]]:
    lowered = f"{workbook_name}:{sheet_name}".lower()
    if "hplc" in lowered:
        return nouvian_hplc_rows(table)
    return nouvian_binary_behaviour_rows(sheet_name, table)


def nouvian_hplc_rows(table: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    if not table:
        return []
    headers = [str(cell).strip() if cell is not None else "" for cell in table[0]]
    normalized = [normalize_header(header) for header in headers]
    if "brain_region" not in normalized:
        return []
    named_headers = [header for header in normalized if header]
    if len(named_headers) != len(set(named_headers)):
        raise ValueError("ambiguous duplicate HPLC headers")
    region_idx = normalized.index("brain_region")
    colony_idx = normalized.index("colony") if "colony" in normalized else None
    odor_idx = normalized.index("odour") if "odour" in normalized else None
    behavior_idx = normalized.index("behaviour") if "behaviour" in normalized else None
    amine_columns = [
        (idx, amine)
        for idx, header in enumerate(headers)
        if (amine := amine_label(header)) is not None
    ]
    amines = [amine for _, amine in amine_columns]
    if len(amines) != len(set(amines)):
        raise ValueError("ambiguous duplicate HPLC amine columns")
    rows: list[dict[str, Any]] = []
    for source_row in table[1:]:
        region = text(source_row[region_idx] if region_idx < len(source_row) else None)
        if not region:
            continue
        stimulus = join_label(
            region,
            text(
                source_row[odor_idx]
                if odor_idx is not None and odor_idx < len(source_row)
                else None
            ),
            text(
                source_row[behavior_idx]
                if behavior_idx is not None and behavior_idx < len(source_row)
                else None
            ),
        )
        colony = text(
            source_row[colony_idx]
            if colony_idx is not None and colony_idx < len(source_row)
            else None
        )
        for idx, amine in amine_columns:
            rows.append(
                {
                    "stimulus": stimulus,
                    "channel": join_label(amine or "amine", colony),
                    "response": source_row[idx] if idx < len(source_row) else None,
                }
            )
    return rows


def nouvian_binary_behaviour_rows(
    sheet_name: str, table: list[tuple[Any, ...]]
) -> list[dict[str, Any]]:
    if len(table) < 2:
        return []
    header_idx = binary_header_index(table)
    if header_idx is None:
        return []
    header = table[header_idx]
    super_header = table[header_idx - 1] if header_idx > 0 else tuple()
    filled_super = fill_forward(tuple(text(cell) for cell in super_header))
    stimuli = {
        idx: text(cell)
        for idx, cell in enumerate(header)
        if idx > 0
        and text(cell)
        and numeric(cell) is None
        and normalize_header(text(cell))
        not in {"note", "notes", "comment", "comments", "annotation", "annotations"}
    }
    column_identities = [
        (stimulus, filled_super[idx] if idx < len(filled_super) else "")
        for idx, stimulus in stimuli.items()
    ]
    if len(column_identities) != len(set(column_identities)):
        raise ValueError("ambiguous duplicate Nouvian condition columns")
    rows: list[dict[str, Any]] = []
    current_row_channel = ""
    for row_index, row in enumerate(table[header_idx + 1 :], start=1):
        label = text(row[0] if row else None)
        if is_nouvian_stats_label(label):
            break
        if label:
            current_row_channel = label
        for idx, stimulus in stimuli.items():
            raw_value = row[idx] if idx < len(row) else None
            value = numeric(raw_value)
            if raw_value not in (None, "", "NA") and value not in (0.0, 1.0):
                raise ValueError("Nouvian binary observations must be 0 or 1")
            column_channel = filled_super[idx] if idx < len(filled_super) else ""
            if column_channel and column_channel.lower() != "odour and treatment":
                channel = join_label(sheet_name, column_channel)
            else:
                channel = join_label(sheet_name, current_row_channel or f"replicate_{row_index}")
            rows.append({"stimulus": stimulus, "channel": channel, "response": value})
    return rows


def binary_header_index(table: list[tuple[Any, ...]]) -> int | None:
    candidates: list[tuple[int, int, int]] = []
    for idx, row in enumerate(table[:4]):
        text_cells = [text(cell) for cell in row[1:] if numeric(cell) is None]
        if sum(bool(cell) for cell in text_cells) >= 2 and any(
            numeric(next_row[col] if col < len(next_row) else None) is not None
            for next_row in table[idx + 1 : idx + 5]
            for col in range(1, min(len(row), len(next_row)))
        ):
            odorish = sum(is_odor_condition_label(cell) for cell in text_cells)
            descriptor = int(any(token in text(row[0]).lower() for token in ("odour", "odor")))
            if odorish or descriptor:
                candidates.append((odorish, descriptor, idx))
    if not candidates:
        return None
    best_score = max(candidate[:2] for candidate in candidates)
    winners = [
        idx for odorish, descriptor, idx in candidates if (odorish, descriptor) == best_score
    ]
    if len(winners) != 1:
        raise ValueError("ambiguous Nouvian condition header")
    return winners[0]


def fill_forward(values: tuple[str, ...]) -> tuple[str, ...]:
    out: list[str] = []
    current = ""
    for value in values:
        current = value or current
        out.append(current)
    return tuple(out)


def amine_label(header: str) -> str | None:
    labels = set(
        re.findall(r"(?<![a-z])(?:octopamine|dopamine|serotonin)(?![a-z])", header.lower())
    )
    if len(labels) > 1:
        raise ValueError("ambiguous HPLC amine identity")
    return next(iter(labels)) if labels else None


def is_odor_condition_label(text_value: str) -> bool:
    return re.search(r"(?<![a-z])(?:tec|iaa)(?![a-z])", text_value.lower()) is not None


def is_nouvian_stats_label(text_value: str) -> bool:
    lowered = text_value.lower()
    return lowered in {
        "mean",
        "<none>",
        "odour",
        "odor",
        "treatment",
        "odour*treatment",
        "odor*treatment",
        "(intercept)",
    } or lowered.startswith("glm")
