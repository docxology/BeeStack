"""Binding guards that keep the research-suite headline honest.

These tests close the oracle gap surfaced by the iteration-10 pre-publication
RedTeam (verifier-specialist V0): the publication-readiness gate certified
``ok:true`` while the abstract headlined ``overall validation fraction of
1.000`` with no caveat, even though the same run catalogued open gaps and an
empirical record well below the completeness threshold. ``overall_validation_
fraction`` is a mean of config-band module self-test booleans, structurally
disconnected from ``known_gaps``; nothing previously bound the headline to the
limitations published in the same run.

The two guards below cannot both hold for the dishonest state (a perfect
self-test rate presented as full validation with no gaps disclosed and no
co-located gap count), but both hold for the current honest framing.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESEARCH_REPORT = PROJECT_ROOT / "output" / "data" / "research_suite_report.json"
ABSTRACT = PROJECT_ROOT / "manuscript" / "00_abstract.md"


def _paragraph_containing(text: str, needle: str) -> str | None:
    """Return the blank-line-delimited paragraph that contains ``needle``."""
    for paragraph in re.split(r"\n\s*\n", text):
        if needle in paragraph:
            return paragraph
    return None


def test_perfect_self_test_rate_requires_disclosed_gaps() -> None:
    """A 1.0 self-test rate must coexist with at least one acknowledged gap.

    Claiming every module self-test passes *and* cataloguing zero limitations
    is the over-claim state. Because the self-test rate is structurally a mean
    of config-band booleans, a perfect rate is uninformative on its own; it is
    only honest when the run still publishes its known gaps.
    """
    report = json.loads(RESEARCH_REPORT.read_text(encoding="utf-8"))
    overall = float(report["overall_validation_fraction"])
    known_gaps = report.get("known_gaps", [])
    if overall >= 1.0:
        assert len(known_gaps) > 0, (
            "overall_validation_fraction is 1.0 but the run catalogues zero "
            "known_gaps: a perfect config-band self-test rate presented with no "
            "acknowledged limitations is an over-claim. Either surface the open "
            "gaps or stop headlining the self-test rate as full validation."
        )


def test_abstract_colocates_self_test_rate_with_gap_count() -> None:
    """The abstract must not headline the self-test rate without the gap count.

    Guards against re-drift back to a bare ``validation fraction of {{...}}``
    sentence. The validation-fraction token and the known-gap-count token must
    appear in the same paragraph, and the disarmed framing must avoid calling
    the bare number a ``validation fraction`` (it is a config-band self-test
    rate, not biological validation).
    """
    text = ABSTRACT.read_text(encoding="utf-8")
    assert "{{RESEARCH_VALIDATION_FRACTION}}" in text, (
        "abstract no longer references the validation-fraction token; update "
        "this guard if the headline was intentionally removed."
    )
    paragraph = _paragraph_containing(text, "{{RESEARCH_VALIDATION_FRACTION}}")
    assert paragraph is not None
    assert "{{RESEARCH_KNOWN_GAP_COUNT}}" in paragraph, (
        "the abstract states the self-test rate without co-locating the "
        "open-gap count in the same paragraph; the headline must never ship "
        "bare (iteration-10 RedTeam finding V-A)."
    )
    assert "validation fraction of {{RESEARCH_VALIDATION_FRACTION}}" not in text, (
        "the abstract uses the bare 'validation fraction of <N>' phrasing that "
        "reads as full biological validation; frame it as a config-band "
        "self-test rate instead."
    )
