"""Write project-wide README/AGENTS signposts and readiness reports."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack.documentation_audit import signposted_directories


@dataclass(frozen=True)
class SignpostWriteResult:
    """Summary of signpost file writes."""

    directory_count: int
    readme_written: tuple[str, ...]
    agents_written: tuple[str, ...]
    missing_readme_dirs: tuple[str, ...]
    missing_agents_dirs: tuple[str, ...]
    passed: bool

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def write_signposts(project_root: Path, *, overwrite: bool = False) -> SignpostWriteResult:
    """Create missing README.md and AGENTS.md files for every non-cache directory."""

    directories = signposted_directories(project_root)
    readme_written: list[str] = []
    agents_written: list[str] = []
    for directory in directories:
        readme_path = directory / "README.md"
        agents_path = directory / "AGENTS.md"
        if overwrite or not readme_path.exists():
            readme_path.write_text(render_readme(project_root, directory), encoding="utf-8")
            readme_written.append(_relative(project_root, readme_path))
        if overwrite or not agents_path.exists():
            agents_path.write_text(render_agents(project_root, directory), encoding="utf-8")
            agents_written.append(_relative(project_root, agents_path))
    missing_readmes = tuple(
        _relative(project_root, directory)
        for directory in directories
        if not (directory / "README.md").exists()
    )
    missing_agents = tuple(
        _relative(project_root, directory)
        for directory in directories
        if not (directory / "AGENTS.md").exists()
    )
    return SignpostWriteResult(
        directory_count=len(directories),
        readme_written=tuple(readme_written),
        agents_written=tuple(agents_written),
        missing_readme_dirs=missing_readmes,
        missing_agents_dirs=missing_agents,
        passed=not missing_readmes and not missing_agents,
    )


def render_readme(project_root: Path, directory: Path) -> str:
    """Render a deterministic README for a directory."""

    context = _directory_context(project_root, directory)
    return "\n".join(
        [
            f"# {context['title']}",
            "",
            str(context["purpose"]),
            "",
            f"- Scope: {context['scope']}",
            f"- Regenerate: {context['regenerate']}",
            f"- Canonical source: {context['canonical_source']}",
            "",
        ]
    )


def render_agents(project_root: Path, directory: Path) -> str:
    """Render deterministic agent instructions for a directory."""

    context = _directory_context(project_root, directory)
    return "\n".join(
        [
            f"# {context['agent_title']}",
            "",
            str(context["agent_guidance"]),
            "",
            f"- Canonical source: {context['canonical_source']}",
            f"- Regeneration command: {context['regenerate']}",
            "",
        ]
    )


def write_project_readiness_review(project_root: Path) -> tuple[Path, Path]:
    """Write project readiness JSON/Markdown reports."""

    reports_dir = project_root / "output" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    coverage = _signposting_payload(project_root)
    audit = _read_json(reports_dir / "documentation_audit.json")
    research = _read_json(reports_dir / "beestack_research_report.json")
    methods = _read_json(project_root / "output" / "data" / "methods_analysis.json")
    synthesis = _read_json(project_root / "output" / "data" / "stack_synthesis_review.json")
    known_gaps = tuple(str(gap) for gap in research.get("known_gaps", ()))
    improvements = _prioritized_improvements(known_gaps)
    payload = {
        "passed": bool(coverage["passed"] and audit.get("passed", False)),
        "signposting": coverage,
        "documentation_audit": {
            "available": bool(audit),
            "passed": bool(audit.get("passed", False)),
            "docs_checked": int(audit.get("docs_checked", 0) or 0),
            "missing_output_paths": tuple(audit.get("missing_output_paths", ())),
            "missing_readme_dirs": tuple(audit.get("missing_readme_dirs", ())),
            "missing_agents_dirs": tuple(audit.get("missing_agents_dirs", ())),
        },
        "methods_analysis": {
            "available": bool(methods),
            "module_count": int(methods.get("module_count", 0) or 0),
            "overall_validation_fraction": float(
                methods.get("overall_validation_fraction", 0.0) or 0.0
            ),
            "figure_count": len(methods.get("figure_paths", ()) or ()),
            "top_validation_gaps": tuple(methods.get("top_validation_gaps", ()) or ()),
        },
        "stack_synthesis": {
            "available": bool(synthesis),
            "validation_fraction": float(synthesis.get("validation_fraction", 0.0) or 0.0),
            "readiness_fraction": float(synthesis.get("readiness_fraction", 0.0) or 0.0),
            "figure_count": len(synthesis.get("figure_paths", ()) or ()),
            "top_findings": tuple(synthesis.get("prioritized_findings", ()) or ())[:3],
        },
        "research_known_gaps": known_gaps,
        "prioritized_improvements": improvements,
    }
    json_path = reports_dir / "project_readiness_review.json"
    md_path = reports_dir / "project_readiness_review.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_readiness_markdown(payload), encoding="utf-8")
    return json_path, md_path


def _signposting_payload(project_root: Path) -> dict[str, object]:
    directories = signposted_directories(project_root)
    missing_readmes = tuple(
        _relative(project_root, directory)
        for directory in directories
        if not (directory / "README.md").exists()
    )
    missing_agents = tuple(
        _relative(project_root, directory)
        for directory in directories
        if not (directory / "AGENTS.md").exists()
    )
    return {
        "directory_count": len(directories),
        "missing_readme_dirs": missing_readmes,
        "missing_agents_dirs": missing_agents,
        "passed": not missing_readmes and not missing_agents,
    }


def _directory_context(project_root: Path, directory: Path) -> dict[str, str]:
    rel = _relative(project_root, directory)
    parts = () if rel == "." else tuple(rel.split("/"))
    generated = parts[:1] == ("output",)
    canonical_source = _canonical_source(parts, generated)
    regenerate = _regeneration_command(parts, generated)
    title, purpose, scope = _title_purpose_scope(parts)
    agent_guidance = _agent_guidance(parts, generated)
    return {
        "title": title,
        "agent_title": rel,
        "purpose": purpose,
        "scope": scope,
        "canonical_source": canonical_source,
        "regenerate": regenerate,
        "agent_guidance": agent_guidance,
    }


def _title_purpose_scope(parts: tuple[str, ...]) -> tuple[str, str, str]:
    rel = "/".join(parts) if parts else "."
    if not parts:
        return (
            "BeeStack Project Root",
            "Top-level BeeStack research project, configuration, documentation, and outputs.",
            "Repository-wide coordination and quickstart guidance.",
        )
    if parts[0] == "src":
        return _source_context(parts)
    if parts[0] == "scripts":
        return (
            "Scripts",
            "Thin orchestration scripts for analysis, downloads, reports, and signposting.",
            "Filesystem I/O and command-line entrypoints.",
        )
    if parts[0] == "tests":
        return ("Tests", "Real-computation test suite for BeeStack.", "Unit and integration tests.")
    if parts[0] == "docs":
        return (
            "Documentation",
            "Research-operations documentation, runbooks, API references, and validation guides.",
            "Human-readable project operations and fidelity language.",
        )
    if parts[0] == "manuscript":
        return (
            "Manuscript",
            "Canonical manuscript source with hydratable variable tokens.",
            "Paper prose and manuscript configuration.",
        )
    if parts[0] == ".github":
        return (
            "GitHub Automation" if len(parts) == 1 else f"GitHub Automation: {parts[-1]}",
            "Repository automation for lint, test, documentation, signposting, and manuscript gates.",
            "CI and repository automation metadata.",
        )
    if parts[0] == ".mplconfig":
        return (
            "Matplotlib Runtime Config",
            "Project-local Matplotlib runtime configuration and font cache for deterministic headless rendering.",
            "Rendering support files; do not treat as scientific source data.",
        )
    if parts[0] == "output":
        return _output_context(parts)
    return (
        rel,
        "BeeStack project directory.",
        "Project support files.",
    )


def _source_context(parts: tuple[str, ...]) -> tuple[str, str, str]:
    module = parts[2] if len(parts) >= 3 and parts[1] == "beestack" else ""
    descriptions = {
        "body": "BeeBody physical simulation, FlyBody adapter, MJCF, and energetics helpers.",
        "brain": "BeeBrain empirical anatomy/activity loaders and reduced AL-MB-CX logic.",
        "digital_twin": "Digital-twin readiness catalog, maturity scoring, and roadmap report rendering.",
        "mind": "BeeMind belief, policy, and expected-free-energy diagnostics.",
        "swarm": "BeeSwarm agents, dances, pheromones, allocation, and colony metrics.",
        "niche": "BeeNiche comb, thermal, forage, and adapter-schema logic.",
        "research": "Typed research-suite scorecards, evidence records, and sensitivity sweeps.",
        "utils": "Small pure utility helpers shared across BeeStack.",
        "visualization": "Figure and animation builders used by scripts.",
    }
    if module:
        return (
            f"src/beestack/{module}",
            descriptions.get(module, "BeeStack package module."),
            "Pure package behavior unless the local README states otherwise.",
        )
    if parts[:2] == ("src", "beestack"):
        return (
            "BeeStack Package",
            "Public Python package for BeeStack contracts and module kernels.",
            "Importable package code.",
        )
    return (
        "Source Tree",
        "Python package source for BeeStack.",
        "Importable source code.",
    )


def _output_context(parts: tuple[str, ...]) -> tuple[str, str, str]:
    rel = "/".join(parts)
    if parts[:3] == ("output", "animations", "flybody_scenes"):
        if len(parts) == 3:
            return (
                "Strict FlyBody Scene Outputs",
                "Generated strict BeeBody 3D MuJoCo scenes for collision and waggle-dance validation.",
                "Regeneratable strict-scene XMLs, contact metrics, body-plan assets, and local signposts.",
            )
        scene = parts[3]
        return (
            f"Strict FlyBody Scene: {scene}",
            "Generated strict BeeBody 3D MuJoCo scene assets and contact telemetry.",
            "Regeneratable strict-scene output for visual and contact validation.",
        )
    if parts[:3] == ("output", "animations", "flybody_bee"):
        if parts[-1] == "assets":
            return (
                "FlyBody BeeBody Assets",
                "Copied FlyBody OBJ/XML assets used by the generated honeybee body plan.",
                "Generated body-plan assets.",
            )
        return (
            "FlyBody BeeBody Plan",
            "Generated `apis_mellifera_worker.xml` body plan and manifest.",
            "Generated BeeBody MJCF assets.",
        )
    if "body_plan" in parts:
        if parts[-1] == "assets":
            return (
                "Scene Body-Plan Assets",
                "Copied BeeBody assets local to a strict MuJoCo scene.",
                "Generated strict-scene assets.",
            )
        return (
            "Scene Body Plan",
            "Generated BeeBody body plan embedded into a strict MuJoCo scene.",
            "Generated strict-scene body plan.",
        )
    if parts[:3] == ("output", "data", "empirical_sources"):
        if len(parts) == 3:
            return (
                "Empirical Sources",
                "Downloaded and cataloged BeeBrain anatomy/activity source payloads.",
                "Regeneratable empirical source cache.",
            )
        dataset = parts[3]
        return (
            f"Empirical Source: {dataset}",
            "Dataset-specific raw payloads, archives, or file-level downloads.",
            "Regeneratable empirical dataset payloads.",
        )
    if parts[:2] == ("output", "diagnostics"):
        return (
            "Output Diagnostics" if len(parts) == 2 else f"Diagnostic Output: {parts[-1]}",
            "Generated diagnostic artifacts for visual, FlyBody, or empirical QA.",
            "Regeneratable diagnostic outputs.",
        )
    output_descriptions = {
        ".checkpoints": "Generated checkpoint metadata for resumable local pipeline runs.",
        "animations": "Generated GIFs, contact sheets, strict-scene XMLs, and animation outputs.",
        "data": "Generated JSON payloads, manifests, empirical analysis, and sensitivity data.",
        "figures": "Generated static figures for analysis, empirical data, and research reports.",
        "interactive": "Generated Plotly HTML research-suite views.",
        "llm": "LLM-assisted research notes and external-analysis transcripts used as audit inputs.",
        "logs": "Local command logs, CI excerpts, and verification transcripts.",
        "manuscript": "Hydrated manuscript sections with variables resolved.",
        "pdf": "Local PDF exports from manuscript or report tooling; ignored except signposts.",
        "reports": "Generated Markdown/JSON reports and audits.",
        "simulations": "Local simulation trace exports and scenario run payloads.",
        "slides": "Local slide exports from manuscript or report tooling; ignored except signposts.",
        "tex": "Local TeX intermediates from manuscript export tooling.",
        "web": "Local web exports or static report bundles; ignored except signposts.",
    }
    if len(parts) >= 2:
        name = parts[1]
        return (
            rel,
            output_descriptions.get(name, "Generated BeeStack output artifact directory."),
            "Regeneratable output artifacts.",
        )
    return (
        "Output",
        "Regeneratable BeeStack artifacts and downloaded empirical payloads.",
        "Generated output tree.",
    )


def _canonical_source(parts: tuple[str, ...], generated: bool) -> str:
    if not generated:
        return "This directory's files are source-of-truth unless local guidance says otherwise."
    if parts[:2] == ("output", ".checkpoints"):
        return "Local pipeline checkpoint writer"
    if parts[:2] == ("output", "animations"):
        return "scripts/generate_animations.py and src/beestack/visualization/"
    if parts[:3] == ("output", "data", "empirical_sources"):
        return "scripts/fetch_empirical_bee_data.py"
    if parts[:2] == ("output", "figures"):
        return "scripts/analysis_pipeline.py or scripts/analyze_empirical_bee_data.py"
    if parts[:2] == ("output", "interactive"):
        return "scripts/run_research_suite.py"
    if parts[:2] == ("output", "llm"):
        return "External-research or LLM-analysis command recorded with each artifact"
    if parts[:2] == ("output", "logs"):
        return "The local command, CI job, or verification run that emitted each log"
    if parts[:2] == ("output", "reports"):
        return "scripts/*.py report writers"
    if parts[:2] == ("output", "manuscript"):
        return "scripts/z_generate_manuscript_variables.py"
    if parts[:2] == ("output", "simulations"):
        return "scripts/analysis_pipeline.py and scenario-specific simulation exporters"
    if parts[:2] == ("output", "tex"):
        return "Manuscript export tooling"
    if parts[:2] in (("output", "pdf"), ("output", "slides"), ("output", "web")):
        return "Local export tooling; artifacts are not part of the core snapshot"
    return "BeeStack scripts and source helpers"


def _regeneration_command(parts: tuple[str, ...], generated: bool) -> str:
    if not generated:
        return "n/a"
    if parts[:2] == ("output", ".checkpoints"):
        return "uv run python scripts/analysis_pipeline.py"
    if parts[:3] == ("output", "data", "empirical_sources"):
        return "uv run python scripts/fetch_empirical_bee_data.py"
    if parts[:2] == ("output", "animations"):
        return "uv run python scripts/generate_animations.py"
    if parts[:2] == ("output", "figures"):
        return "uv run python scripts/analysis_pipeline.py"
    if parts[:2] == ("output", "interactive"):
        return "uv run python scripts/run_research_suite.py"
    if parts[:2] in (("output", "llm"), ("output", "logs")):
        return "rerun the recorded command that produced the artifact"
    if parts[:2] == ("output", "manuscript"):
        return "uv run python scripts/z_generate_manuscript_variables.py"
    if parts[:2] == ("output", "reports"):
        return "uv run python scripts/analysis_pipeline.py"
    if parts[:2] == ("output", "simulations"):
        return "uv run python scripts/analysis_pipeline.py"
    if parts[:2] == ("output", "tex"):
        return "manuscript export command used for the local build"
    if parts[:2] in (("output", "pdf"), ("output", "slides"), ("output", "web")):
        return "local export command; not part of core CI"
    return "uv run python scripts/analysis_pipeline.py"


def _agent_guidance(parts: tuple[str, ...], generated: bool) -> str:
    if generated:
        if parts[:3] == ("output", "animations", "flybody_scenes"):
            return (
                "Generated strict FlyBody/MuJoCo scene area. Preserve contact metrics, "
                "body-plan provenance, and backend/fidelity wording; change scene logic "
                "in source helpers and regenerate through the animation scripts."
            )
        if parts[:2] in (("output", "pdf"), ("output", "slides"), ("output", "web")):
            return (
                "Local export artifact area. Keep README/AGENTS signposts, but do not "
                "treat exported PDFs, slides, or web bundles as canonical manuscript source."
            )
        if parts[:2] in (("output", "llm"), ("output", "logs")):
            return (
                "Generated audit-evidence area. Preserve prompts, source URLs, commands, "
                "timestamps, and verification context when adding artifacts here."
            )
        return (
            "Generated or downloaded artifact area. Do not hand-edit scientific outputs; "
            "change the producing script or source helper and regenerate."
        )
    if parts[:1] == (".mplconfig",):
        return (
            "Project-local Matplotlib support area. Keep render configuration deterministic; "
            "do not treat font-cache JSON as scientific evidence."
        )
    return (
        "Project source area. Preserve the research-template separation between "
        "pure source behavior, script I/O, tests, manuscript prose, and output artifacts."
    )


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _prioritized_improvements(known_gaps: tuple[str, ...]) -> tuple[dict[str, object], ...]:
    candidates = [
        (
            "BeeBrain calcium acquisition completion",
            "Resolve missing Paoli MATLAB calcium local payloads and verify HDF5/MAT parsing.",
            "BeeBrain",
            5,
            4,
            3,
        ),
        (
            "BeeBody inertial calibration",
            "Calibrate generated honeybee mass, inertia, and articulated topology against biomechanics data.",
            "BeeBody",
            5,
            5,
            5,
        ),
        (
            "BeeSwarm population adapter validation",
            "Compare reduced colony summaries against BEEHAVE-compatible scenario tables.",
            "BeeSwarm",
            4,
            4,
            4,
        ),
        (
            "BeeNiche forage calibration",
            "Calibrate deterministic weather/nectar seasonality witnesses against external forage observations.",
            "BeeNiche",
            4,
            3,
            3,
        ),
        (
            "BeeMind transition-model calibration",
            "Replace hand-calibrated expected-free-energy witnesses with fitted transition terms.",
            "BeeMind",
            4,
            3,
            4,
        ),
        (
            "Documentation source freshness watch",
            "Periodically refresh external source links, generated artifacts, and fidelity language.",
            "Docs",
            3,
            3,
            2,
        ),
    ]
    rows = []
    for title, rationale, module, impact, risk, effort in candidates:
        rows.append(
            {
                "title": title,
                "module": module,
                "rationale": rationale,
                "impact": impact,
                "risk": risk,
                "effort": effort,
                "priority": (impact + risk) * (6 - effort),
                "related_known_gap_count": sum(
                    1 for gap in known_gaps if module.lower().replace("bee", "") in gap.lower()
                ),
            }
        )
    return tuple(sorted(rows, key=lambda row: (-int(row["priority"]), str(row["title"]))))


def _readiness_markdown(payload: dict[str, Any]) -> str:
    signposting = payload["signposting"]
    audit = payload["documentation_audit"]
    methods = payload["methods_analysis"]
    synthesis = payload["stack_synthesis"]
    lines = [
        "# BeeStack Project Readiness Review",
        "",
        f"- Passed: `{payload['passed']}`",
        f"- Signposted directories: `{signposting['directory_count']}`",
        f"- Signposting passed: `{signposting['passed']}`",
        f"- Documentation audit available: `{audit['available']}`",
        f"- Documentation audit passed: `{audit['passed']}`",
        f"- Methods analysis available: `{methods['available']}`",
        f"- Methods validation fraction: `{methods['overall_validation_fraction']:.3f}`",
        f"- Methods figure count: `{methods['figure_count']}`",
        f"- Stack synthesis available: `{synthesis['available']}`",
        f"- Stack synthesis validation fraction: `{synthesis['validation_fraction']:.3f}`",
        f"- Stack synthesis readiness fraction: `{synthesis['readiness_fraction']:.3f}`",
        f"- Stack synthesis figure count: `{synthesis['figure_count']}`",
        "",
        "## Signposting Gaps",
        "",
    ]
    if signposting["missing_readme_dirs"] or signposting["missing_agents_dirs"]:
        lines.extend(f"- Missing README: `{path}`" for path in signposting["missing_readme_dirs"])
        lines.extend(f"- Missing AGENTS: `{path}`" for path in signposting["missing_agents_dirs"])
    else:
        lines.append("- None detected.")
    lines.extend(["", "## Stack Synthesis Findings", ""])
    if synthesis["top_findings"]:
        lines.extend(f"- {finding}" for finding in synthesis["top_findings"])
    else:
        lines.append("- No stack-synthesis findings were available.")
    lines.extend(["", "## Prioritized Improvements", ""])
    for item in payload["prioritized_improvements"]:
        lines.append(
            f"- P{item['priority']} `{item['module']}` {item['title']}: {item['rationale']}"
        )
    lines.extend(["", "## Methods Analysis Gaps", ""])
    if methods["top_validation_gaps"]:
        lines.extend(f"- {gap}" for gap in methods["top_validation_gaps"])
    else:
        lines.append("- No methods-analysis gaps were available.")
    lines.extend(["", "## Research Known Gaps", ""])
    if payload["research_known_gaps"]:
        lines.extend(f"- {gap}" for gap in payload["research_known_gaps"])
    else:
        lines.append("- No research-suite known gaps were available.")
    lines.append("")
    return "\n".join(lines)


def _relative(project_root: Path, path: Path) -> str:
    relative = path.resolve().relative_to(project_root.resolve())
    return "." if not relative.parts else relative.as_posix()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--check", action="store_true", help="Check coverage without writing.")
    parser.add_argument("--overwrite", action="store_true", help="Rewrite existing signposts.")
    args = parser.parse_args()

    if args.check:
        payload = _signposting_payload(args.project_root)
        print(json.dumps(payload, indent=2, sort_keys=True))
        if not payload["passed"]:
            raise SystemExit("BeeStack signposting check failed")
        return
    result = write_signposts(args.project_root, overwrite=args.overwrite)
    write_project_readiness_review(args.project_root)
    print(json.dumps(result.as_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
