from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT_DIR = PROJECT_ROOT / "docs" / "manuscript"
H1_RE = re.compile(r"^# .+\{#sec:[^}]+\}\s*$")
FIG_LABEL_RE = re.compile(r"\{#fig:([^}\s]+)")
FIG_REF_RE = re.compile(r"(?:\[@fig:|@fig:)([^\]}\s]+)")
FORBIDDEN_LATEX_RE = re.compile(r"\\(?:cite|ref|eqref)\{")


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
