"""Security posture audit for the BeeStack research package."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .url_policy import audit_registered_download_urls

_FORBIDDEN_SRC_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("shell=True subprocess", re.compile(r"shell\s*=\s*True")),
    ("unsafe yaml.load", re.compile(r"yaml\.load\s*\(")),
    ("pickle.loads", re.compile(r"pickle\.loads\s*\(")),
    ("eval(", re.compile(r"\beval\s*\(")),
)


@dataclass(frozen=True)
class SecurityPostureAudit:
    """Summary of static security posture checks for BeeStack."""

    threat_model_present: bool
    security_doc_present: bool
    uv_lock_present: bool
    registry_url_violations: tuple[str, ...]
    forbidden_pattern_hits: tuple[str, ...]
    urllib_modules: tuple[str, ...]
    passed: bool

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def audit_security_posture(project_root: Path) -> SecurityPostureAudit:
    """Run repository-local security posture checks."""

    threat_model = project_root / "BeeStack-threat-model.md"
    security_doc = project_root / "docs" / "security_posture.md"
    uv_lock_present = (project_root / "uv.lock").is_file()
    registry_violations = audit_registered_download_urls()
    forbidden_hits = _scan_forbidden_patterns(project_root / "src")
    forbidden_hits += _scan_forbidden_patterns(project_root / "scripts")
    urllib_modules = _urllib_modules(project_root / "src")
    passed = (
        threat_model.is_file()
        and security_doc.is_file()
        and uv_lock_present
        and not registry_violations
        and not forbidden_hits
        and urllib_modules == ("beestack/brain/empirical_fetch.py",)
    )
    return SecurityPostureAudit(
        threat_model_present=threat_model.is_file(),
        security_doc_present=security_doc.is_file(),
        uv_lock_present=uv_lock_present,
        registry_url_violations=registry_violations,
        forbidden_pattern_hits=tuple(sorted(set(forbidden_hits))),
        urllib_modules=urllib_modules,
        passed=passed,
    )


def security_posture_markdown(audit: SecurityPostureAudit) -> str:
    """Render the posture audit as Markdown."""

    status = "passed" if audit.passed else "failed"
    lines = [
        "# BeeStack security posture audit",
        "",
        f"Status: **{status}**",
        "",
        "## Checks",
        "",
        f"- Threat model present: `{audit.threat_model_present}`",
        f"- Security operations doc present: `{audit.security_doc_present}`",
        f"- uv.lock present (supply-chain pin): `{audit.uv_lock_present}`",
        f"- Registry URL violations: `{len(audit.registry_url_violations)}`",
        f"- Forbidden pattern hits: `{len(audit.forbidden_pattern_hits)}`",
        f"- urllib modules under `src/`: `{', '.join(audit.urllib_modules) or 'none'}`",
        "",
    ]
    if audit.registry_url_violations:
        lines.extend(["## Registry URL violations", ""])
        lines.extend(f"- `{url}`" for url in audit.registry_url_violations)
        lines.append("")
    if audit.forbidden_pattern_hits:
        lines.extend(["## Forbidden pattern hits", ""])
        lines.extend(f"- `{hit}`" for hit in audit.forbidden_pattern_hits)
        lines.append("")
    lines.extend(
        [
            "## Operational notes",
            "",
            "BeeStack is an offline research CLI. Network fetch is confined to",
            "`beestack.brain.empirical_fetch` with HTTPS host allowlisting.",
            "See `docs/security_posture.md` and `BeeStack-threat-model.md`.",
            "",
        ]
    )
    return "\n".join(lines)


def _scan_forbidden_patterns(root: Path) -> list[str]:
    hits: list[str] = []
    if not root.exists():
        return hits
    for path in sorted(root.rglob("*.py")):
        if "beestack/security" in path.as_posix():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(root.parent).as_posix()
        for label, pattern in _FORBIDDEN_SRC_PATTERNS:
            if pattern.search(text):
                hits.append(f"{rel}:{label}")
    return hits


def _urllib_modules(src_root: Path) -> tuple[str, ...]:
    pattern = re.compile(r"(?:^|\n)\s*(?:import urllib\.(?:request|error)|from urllib)")
    modules: list[str] = []
    for path in sorted(src_root.rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if pattern.search(text):
            modules.append(path.relative_to(src_root).as_posix())
    return tuple(modules)
