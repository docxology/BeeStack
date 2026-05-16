"""Documentation freshness and fidelity-claim audit helpers."""

from __future__ import annotations

import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path

EXCLUDED_SIGNPOST_DIR_NAMES = frozenset(
    {".git", ".venv", ".pytest_cache", ".ruff_cache", "htmlcov", "__pycache__"}
)


@dataclass(frozen=True)
class DocumentationAudit:
    """Summary of documentation completeness and generated-output references."""

    docs_checked: int
    command_count: int
    source_link_count: int
    output_reference_count: int
    unresolved_variable_count: int
    directory_count: int
    missing_output_paths: tuple[str, ...]
    missing_readme_dirs: tuple[str, ...]
    missing_agents_dirs: tuple[str, ...]
    signposting_passed: bool
    fidelity_claims: tuple[str, ...]
    passed: bool

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def audit_documentation(project_root: Path) -> DocumentationAudit:
    """Audit README, docs, manuscript, and script docs for current run integrity."""

    documents = _documentation_files(project_root)
    combined = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in documents)
    commands = re.findall(r"uv run [^\n`]+", combined)
    links = re.findall(r"https?://[^\s)>\"]+", combined)
    output_refs = tuple(
        sorted({ref.rstrip(".,;:)") for ref in re.findall(r"output/[A-Za-z0-9_./-]+", combined)})
    )
    missing = tuple(ref for ref in output_refs if not (project_root / ref).exists())
    signposted_dirs = signposted_directories(project_root)
    missing_readmes = tuple(
        _relative_dir(project_root, directory)
        for directory in signposted_dirs
        if not (directory / "README.md").exists()
    )
    missing_agents = tuple(
        _relative_dir(project_root, directory)
        for directory in signposted_dirs
        if not (directory / "AGENTS.md").exists()
    )
    signposting_passed = not missing_readmes and not missing_agents
    resolved_manuscript = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted((project_root / "output" / "manuscript").glob("*.md"))
    )
    unresolved = re.findall(r"\{\{[A-Z0-9_]+\}\}", resolved_manuscript)
    fidelity_claims = tuple(
        sorted(
            {line.strip("- ").strip() for line in combined.splitlines() if _is_fidelity_line(line)}
        )
    )
    passed = (
        len(documents) >= 8
        and len(commands) >= 8
        and len(links) >= 4
        and not unresolved
        and not missing
        and signposting_passed
        and len(fidelity_claims) >= 3
    )
    return DocumentationAudit(
        docs_checked=len(documents),
        command_count=len(commands),
        source_link_count=len(links),
        output_reference_count=len(output_refs),
        unresolved_variable_count=len(unresolved),
        directory_count=len(signposted_dirs),
        missing_output_paths=missing,
        missing_readme_dirs=missing_readmes,
        missing_agents_dirs=missing_agents,
        signposting_passed=signposting_passed,
        fidelity_claims=fidelity_claims,
        passed=passed,
    )


def documentation_audit_markdown(audit: DocumentationAudit) -> str:
    """Render a documentation audit as Markdown."""

    lines = [
        "# BeeStack Documentation Audit",
        "",
        f"- Passed: `{audit.passed}`",
        f"- Documents checked: `{audit.docs_checked}`",
        f"- `uv run` commands referenced: `{audit.command_count}`",
        f"- Source links referenced: `{audit.source_link_count}`",
        f"- Generated-output paths referenced: `{audit.output_reference_count}`",
        f"- Unresolved manuscript variables: `{audit.unresolved_variable_count}`",
        f"- Signposted directories: `{audit.directory_count}`",
        f"- Signposting passed: `{audit.signposting_passed}`",
        "",
        "## Fidelity Language",
        "",
    ]
    lines.extend(f"- {claim}" for claim in audit.fidelity_claims)
    lines.extend(["", "## Missing Output References", ""])
    if audit.missing_output_paths:
        lines.extend(f"- `{path}`" for path in audit.missing_output_paths)
    else:
        lines.append("- None detected.")
    lines.extend(["", "## Missing README Files", ""])
    if audit.missing_readme_dirs:
        lines.extend(f"- `{path}/README.md`" for path in audit.missing_readme_dirs)
    else:
        lines.append("- None detected.")
    lines.extend(["", "## Missing AGENTS Files", ""])
    if audit.missing_agents_dirs:
        lines.extend(f"- `{path}/AGENTS.md`" for path in audit.missing_agents_dirs)
    else:
        lines.append("- None detected.")
    lines.append("")
    return "\n".join(lines)


def signposted_directories(project_root: Path) -> tuple[Path, ...]:
    """Return non-cache project directories expected to carry signpost files."""

    project_root = project_root.resolve()
    directories: list[Path] = []
    for root, dir_names, _ in os.walk(project_root):
        root_path = Path(root)
        dir_names[:] = [
            name
            for name in sorted(dir_names)
            if not _is_excluded_signpost_dir(root_path / name, project_root)
        ]
        if not _is_excluded_signpost_dir(root_path, project_root):
            directories.append(root_path)
    return tuple(directories)


def _is_excluded_signpost_dir(directory: Path, project_root: Path) -> bool:
    if directory == project_root:
        return False
    if directory.name in EXCLUDED_SIGNPOST_DIR_NAMES:
        return True
    return directory.name.endswith(".egg-info")


def _relative_dir(project_root: Path, directory: Path) -> str:
    relative = directory.resolve().relative_to(project_root.resolve())
    return "." if not relative.parts else relative.as_posix()


def _documentation_files(project_root: Path) -> tuple[Path, ...]:
    roots = (
        project_root / "README.md",
        project_root / "docs",
        project_root / "manuscript",
        project_root / "scripts" / "README.md",
        project_root / "output" / "README.md",
        project_root / "output" / "reports" / "README.md",
    )
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(sorted(root.glob("*.md")))
    return tuple(path for path in files if path.exists())


def _is_fidelity_line(line: str) -> bool:
    lowered = line.lower()
    return any(
        token in lowered
        for token in (
            "real flybody",
            "reduced",
            "not a full",
            "does not claim",
            "downloaded",
            "empirical",
        )
    )
