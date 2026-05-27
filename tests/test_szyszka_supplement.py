"""Tests for Szyszka MDPI supplementary Table S1 parsing."""

from __future__ import annotations

from beestack.brain.empirical_parsers.szyszka import ODOR_LABELS, parse_table_s1_text

TABLE_S1_SNIPPET = """
Supplementary Table S1. Statistical test on best-match-to-template tests.
1HEX
0.0001
0.0004
119
0.013
0.020
103
3HEX
0.0016
0.0032
99
0.0022
0.0044
98
"""


def test_parse_table_s1_text_extracts_wilcoxon_triplets() -> None:
    rows = parse_table_s1_text(TABLE_S1_SNIPPET)
    assert rows
    assert {row.odor for row in rows} <= set(ODOR_LABELS)
    first = rows[0]
    assert first.odor == "1HEX"
    assert first.original_p == 0.0001
    assert first.fdr_p == 0.0004
    assert first.signed_rank_w == 119
