from __future__ import annotations

import re
from pathlib import Path

from beestack.visualization.figure_registry import (
    FIGURE_NARRATIVES,
    manuscript_image_markdown,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT_DIR = PROJECT_ROOT / "manuscript"
IMAGE_RE = re.compile(r"!\[[^\]]*\]\((?P<path>[^)]+)\)\{#(?P<label>[^}\s]+(?:\s+[^}]+)?)\}")
H1_RE = re.compile(r"^# .+\{#sec:[^}]+\}\s*$")
FIG_LABEL_RE = re.compile(r"\{#fig:([^}\s]+)")
FIG_REF_RE = re.compile(r"(?:\[@fig:|@fig:)([^\]}\s]+)")
FORBIDDEN_LATEX_RE = re.compile(r"\\(?:cite|ref|eqref)\{")


def test_primary_manuscript_figures_match_registry_markdown() -> None:
    by_label = {
        narrative.manuscript_label: manuscript_image_markdown(narrative)
        for narrative in FIGURE_NARRATIVES
        if narrative.priority == "primary"
    }
    for markdown_path in sorted(MANUSCRIPT_DIR.glob("[0-9][0-9]_*.md")):
        text = markdown_path.read_text(encoding="utf-8")
        for match in IMAGE_RE.finditer(text):
            label = match.group("label").split()[0]
            assert label in by_label, f"{markdown_path.name} references unknown label {label}"
            assert match.group(0) == by_label[label], f"{markdown_path.name} drift for {label}"


def test_primary_figure_captions_avoid_machine_flag_literals() -> None:
    forbidden = ("DIGITAL_TWIN_READY=", "_READY=", "False`")
    for narrative in FIGURE_NARRATIVES:
        if narrative.priority != "primary":
            continue
        line = manuscript_image_markdown(narrative)
        for token in forbidden:
            assert token not in line, f"{narrative.manuscript_label} contains {token}"


def test_primary_figure_captions_and_alt_text_stay_reader_directed() -> None:
    for narrative in FIGURE_NARRATIVES:
        if narrative.priority != "primary":
            continue
        caption = narrative.manuscript_contract_caption()
        assert len(caption) <= 520, narrative.manuscript_label
        assert "Generated from" in caption, narrative.manuscript_label
        assert "Sidecar validation" in caption, narrative.manuscript_label
        assert len(narrative.alt_text) <= 180, narrative.manuscript_label
        assert "Generated from" not in narrative.alt_text, narrative.manuscript_label
        assert "Sidecar validation" not in narrative.alt_text, narrative.manuscript_label


def test_manuscript_h2_headings_use_sentence_case() -> None:
    allow_title_case = {
        "14_roadmap.md",
    }
    module_tokens = (
        "BeeStack",
        "BeeBody",
        "BeeBrain",
        "BeeMind",
        "BeeSwarm",
        "BeeNiche",
        "BEEHAVE",
        "FlyBody",
        "MuJoCo",
    )
    title_case_re = re.compile(r"^## [A-Z][a-z]+ [A-Z]")
    for markdown_path in sorted(MANUSCRIPT_DIR.glob("[0-9][0-9]_*.md")):
        if markdown_path.name in allow_title_case:
            continue
        for line in markdown_path.read_text(encoding="utf-8").splitlines():
            if not title_case_re.match(line):
                continue
            if any(token in line for token in module_tokens):
                continue
            raise AssertionError(f"{markdown_path.name} title-case H2: {line}")


def test_numbered_manuscript_h1s_carry_section_labels() -> None:
    for markdown_path in sorted(MANUSCRIPT_DIR.glob("[0-9][0-9]_*.md")):
        lines = markdown_path.read_text(encoding="utf-8").splitlines()
        h1_lines = [line for line in lines if line.startswith("# ") and not line.startswith("## ")]
        assert h1_lines, f"{markdown_path.name} missing H1"
        assert H1_RE.match(h1_lines[0]), f"{markdown_path.name} H1 lacks {{#sec:…}}: {h1_lines[0]}"


def test_every_figure_label_has_prose_reference_in_same_file() -> None:
    for markdown_path in sorted(MANUSCRIPT_DIR.glob("[0-9][0-9]_*.md")):
        text = markdown_path.read_text(encoding="utf-8")
        labels = {match.group(1) for match in FIG_LABEL_RE.finditer(text)}
        refs = {match.group(1) for match in FIG_REF_RE.finditer(text)}
        missing = sorted(labels - refs)
        assert not missing, f"{markdown_path.name} missing prose refs for {missing}"


def test_manuscript_source_bans_raw_latex_cite_and_ref_macros() -> None:
    for markdown_path in sorted(MANUSCRIPT_DIR.glob("[0-9][0-9]_*.md")):
        text = markdown_path.read_text(encoding="utf-8")
        match = FORBIDDEN_LATEX_RE.search(text)
        assert match is None, f"{markdown_path.name} contains forbidden macro {match.group(0)}"
