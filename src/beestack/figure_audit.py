"""Pure manuscript-figure audit helpers."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .visualization.figure_registry import high_priority_figure_artifacts

_MANUSCRIPT_AUDIT_SKIP = frozenset({"README.md", "SYNTAX.md", "AGENTS.md"})
_IMAGE_RE = re.compile(
    r"!\[(?P<caption>[^\]]*)\]\((?P<path>[^)]+)\)\{#fig:(?P<label>[^}\s]+)[^}]*\}"
)
_POSITIVE_CLAIM_RE = re.compile(r"\b(supports?|validates?|validated|proves?|confirms?)\b", re.I)
_REQUIRED_SIDECAR_FIELDS = (
    "caption",
    "alt_text",
    "manuscript_section",
    "manuscript_label",
    "claim_tier",
    "unsupported_inference",
    "artifact_kind",
    "source_data",
    "regeneration_command",
)


@dataclass(frozen=True)
class FigureAudit:
    """Audit hydrated manuscript image references against generated artifacts."""

    image_reference_count: int
    missing_image_paths: tuple[str, ...]
    missing_labels: tuple[str, ...]
    duplicate_labels: tuple[str, ...]
    missing_captions: tuple[str, ...]
    missing_sidecar_paths: tuple[str, ...]
    missing_high_priority_artifacts: tuple[str, ...]
    absent_positive_claims: tuple[str, ...]
    sidecar_required_field_failures: tuple[str, ...] = ()
    sidecar_manuscript_mismatches: tuple[str, ...] = ()
    primary_caption_contract_failures: tuple[str, ...] = ()
    absolute_path_leaks: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return not (
            self.missing_image_paths
            or self.missing_labels
            or self.duplicate_labels
            or self.missing_captions
            or self.missing_sidecar_paths
            or self.missing_high_priority_artifacts
            or self.absent_positive_claims
            or self.sidecar_required_field_failures
            or self.sidecar_manuscript_mismatches
            or self.primary_caption_contract_failures
            or self.absolute_path_leaks
        )

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["passed"] = self.passed
        return payload


@dataclass(frozen=True)
class FigureReference:
    """One Markdown image reference in a hydrated manuscript file."""

    markdown_path: Path
    caption: str
    relative_path: str
    label: str
    resolved_path: Path
    line: str

    def artifact_path(self, project_root: Path) -> str:
        try:
            return self.resolved_path.resolve().relative_to(project_root.resolve()).as_posix()
        except ValueError:
            return self.resolved_path.as_posix()


def audit_figures(
    project_root: Path,
    *,
    required_primary_artifacts: tuple[str, ...] | None = None,
    absent_artifacts: tuple[str, ...] = (),
) -> FigureAudit:
    """Check hydrated manuscript figure references and curated registry coverage."""

    project_root = project_root.resolve()
    references = _manuscript_image_references(project_root)
    missing_images: list[str] = []
    missing_labels: list[str] = []
    missing_captions: list[str] = []
    missing_sidecars: list[str] = []
    labels: list[str] = []
    referenced_artifacts: set[str] = set()
    references_by_artifact: dict[str, FigureReference] = {}
    absent_positive_claims: list[str] = []
    absent_set = set(absent_artifacts)

    for reference in references:
        label = reference.label
        if not label:
            missing_labels.append(_reference_id(project_root, reference))
        else:
            labels.append(label)
        if not reference.caption.strip():
            missing_captions.append(_reference_id(project_root, reference))
        if not reference.resolved_path.exists():
            missing_images.append(_reference_id(project_root, reference))
            continue
        artifact = reference.artifact_path(project_root)
        referenced_artifacts.add(artifact)
        references_by_artifact[artifact] = reference
        if reference.resolved_path.suffix.lower() == ".png":
            sidecar = reference.resolved_path.with_suffix(".json")
            if not sidecar.exists():
                missing_sidecars.append(_relative(project_root, sidecar))
        if artifact in absent_set and _POSITIVE_CLAIM_RE.search(reference.line):
            absent_positive_claims.append(
                f"{_relative(project_root, reference.markdown_path)}:{reference.line.strip()}"
            )

    duplicate_labels = tuple(sorted({label for label in labels if labels.count(label) > 1}))
    required = (
        high_priority_figure_artifacts()
        if required_primary_artifacts is None
        else required_primary_artifacts
    )
    missing_primary = tuple(
        artifact for artifact in required if artifact not in referenced_artifacts
    )
    (
        sidecar_required,
        sidecar_mismatches,
        primary_caption_failures,
        absolute_path_leaks,
    ) = _audit_sidecars(project_root, references_by_artifact)
    return FigureAudit(
        image_reference_count=len(references),
        missing_image_paths=tuple(sorted(dict.fromkeys(missing_images))),
        missing_labels=tuple(sorted(dict.fromkeys(missing_labels))),
        duplicate_labels=duplicate_labels,
        missing_captions=tuple(sorted(dict.fromkeys(missing_captions))),
        missing_sidecar_paths=tuple(sorted(dict.fromkeys(missing_sidecars))),
        missing_high_priority_artifacts=missing_primary,
        absent_positive_claims=tuple(sorted(dict.fromkeys(absent_positive_claims))),
        sidecar_required_field_failures=sidecar_required,
        sidecar_manuscript_mismatches=sidecar_mismatches,
        primary_caption_contract_failures=primary_caption_failures,
        absolute_path_leaks=absolute_path_leaks,
    )


def _manuscript_image_references(project_root: Path) -> tuple[FigureReference, ...]:
    manuscript_dir = project_root / "output" / "manuscript"
    references: list[FigureReference] = []
    for markdown_path in sorted(manuscript_dir.glob("*.md")):
        if markdown_path.name in _MANUSCRIPT_AUDIT_SKIP:
            continue
        for line in markdown_path.read_text(encoding="utf-8", errors="replace").splitlines():
            for match in _IMAGE_RE.finditer(line):
                relative = match.group("path")
                references.append(
                    FigureReference(
                        markdown_path=markdown_path,
                        caption=match.group("caption"),
                        relative_path=relative,
                        label=match.group("label") or "",
                        resolved_path=(markdown_path.parent / relative).resolve(),
                        line=line,
                    )
                )
    return tuple(references)


def _reference_id(project_root: Path, reference: FigureReference) -> str:
    return f"{_relative(project_root, reference.markdown_path)}:{reference.relative_path}"


def _audit_sidecars(
    project_root: Path,
    references_by_artifact: dict[str, FigureReference],
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    required_failures: list[str] = []
    mismatches: list[str] = []
    primary_caption_failures: list[str] = []
    absolute_leaks: list[str] = []
    for sidecar in sorted((project_root / "output" / "figures").rglob("*.json")):
        sidecar_id = _relative(project_root, sidecar)
        try:
            payload = json.loads(sidecar.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            required_failures.append(f"{sidecar_id}:invalid_json")
            continue
        absolute_leaks.extend(_absolute_path_leaks(project_root, sidecar_id, payload))
        if not _is_metadata_sidecar(sidecar, payload):
            continue
        for field in _REQUIRED_SIDECAR_FIELDS:
            if not payload.get(field):
                required_failures.append(f"{sidecar_id}:{field}")
        figure_path = sidecar.with_suffix(".png")
        artifact = _relative(project_root, figure_path)
        reference = references_by_artifact.get(artifact)
        if reference is None:
            continue
        if str(payload.get("priority", "")) == "indexed":
            continue
        sidecar_label = str(payload.get("manuscript_label", ""))
        reference_label = (
            reference.label if reference.label.startswith("fig:") else f"fig:{reference.label}"
        )
        if sidecar_label != reference_label:
            mismatches.append(f"{sidecar_id}:manuscript_label")
        sidecar_caption = str(payload.get("caption", ""))
        if sidecar_caption and not _captions_agree(sidecar_caption, reference.caption):
            mismatches.append(f"{sidecar_id}:caption")
        if str(payload.get("priority", "")) == "primary" and not _primary_caption_contract_ok(
            reference.caption, payload
        ):
            primary_caption_failures.append(f"{sidecar_id}:caption_contract")
    return (
        tuple(sorted(dict.fromkeys(required_failures))),
        tuple(sorted(dict.fromkeys(mismatches))),
        tuple(sorted(dict.fromkeys(primary_caption_failures))),
        tuple(sorted(dict.fromkeys(absolute_leaks))),
    )


def _is_metadata_sidecar(sidecar: Path, payload: dict[str, object]) -> bool:
    """Return True for narrative metadata sidecars, not raw plot-data JSON."""

    schema = str(payload.get("schema", ""))
    if schema == "beestack.figure_data.v1" or sidecar.name.endswith("_data.json"):
        return False
    return schema == "beestack.figure.v1" or sidecar.with_suffix(".png").exists()


def _absolute_path_leaks(project_root: Path, sidecar_id: str, payload: object) -> tuple[str, ...]:
    leaks: list[str] = []
    root_text = project_root.resolve().as_posix()

    def visit(value: object, key_path: str) -> None:
        if isinstance(value, str):
            if value.startswith(root_text):
                leaks.append(f"{sidecar_id}:{key_path}")
            return
        if isinstance(value, dict):
            for key, nested in value.items():
                visit(nested, f"{key_path}.{key}" if key_path else str(key))
            return
        if isinstance(value, list | tuple):
            for index, nested in enumerate(value):
                visit(nested, f"{key_path}[{index}]")

    visit(payload, "")
    return tuple(leaks)


def _captions_agree(sidecar_caption: str, manuscript_caption: str) -> bool:
    sidecar_tokens = set(_caption_tokens(sidecar_caption))
    manuscript_tokens = set(_caption_tokens(manuscript_caption))
    if not sidecar_tokens:
        return True
    overlap = sidecar_tokens & manuscript_tokens
    return len(overlap) >= min(2, len(sidecar_tokens))


def _primary_caption_contract_ok(caption: str, sidecar: dict[str, object]) -> bool:
    lowered = caption.lower()
    backend = (
        str(sidecar.get("backend", ""))
        .replace("/", " ")
        .replace("+", " ")
        .split(maxsplit=1)[0]
        .lower()
    )
    has_backend = bool(backend) and backend in lowered
    has_source = "generated from" in lowered or "generated by" in lowered
    has_validation = "validation" in lowered or "sidecar" in lowered
    has_boundary = "rather than" in lowered or "does not" in lowered or "not " in lowered
    return has_backend and has_source and has_validation and has_boundary


def _caption_tokens(caption: str) -> tuple[str, ...]:
    stopwords = {
        "and",
        "from",
        "into",
        "that",
        "the",
        "this",
        "with",
    }
    return tuple(
        token
        for token in re.findall(r"[a-z0-9]+", caption.lower().replace("timeseries", "time series"))
        if len(token) > 2 and token not in stopwords
    )


def _relative(project_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()
