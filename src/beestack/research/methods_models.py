"""Methods-analysis dataclasses for BeeStack."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from ..utils import project_relative_path
from ..visualization.figure_registry import (
    figure_narrative_for_path,
)
from .methods_helpers import _looks_like_doi, _path_is_figure
from .methods_validators import _validate_metric_map, _validate_numeric_sequence
from .suite import EVIDENCE_AVAILABILITY_STATES, ResearchValidationRecord


@dataclass(frozen=True)
class ManuscriptEvidenceLink:
    """Link one manuscript claim to a generated artifact and variables."""

    module: str
    manuscript_section: str
    artifact_path: str
    evidence_type: str
    claim: str
    regeneration_command: str
    variable_tokens: tuple[str, ...]
    availability_status: str = "generated"
    citation_keys: tuple[str, ...] = ()
    source_dois: tuple[str, ...] = ()
    artifact_kind: str = ""
    claim_tier: str = ""

    def __post_init__(self) -> None:
        for field_name, value in asdict(self).items():
            if field_name in {"variable_tokens", "citation_keys", "source_dois"}:
                if not value:
                    raise ValueError(f"manuscript evidence link needs at least one {field_name}")
                if not all(isinstance(token, str) and token for token in value):
                    raise ValueError(f"manuscript evidence {field_name} values must be nonempty")
            elif field_name == "availability_status":
                if value not in EVIDENCE_AVAILABILITY_STATES:
                    raise ValueError(
                        "manuscript evidence availability_status must be one of "
                        f"{', '.join(sorted(EVIDENCE_AVAILABILITY_STATES))}"
                    )
            elif not isinstance(value, str) or not value:
                raise ValueError(f"manuscript evidence {field_name} must be nonempty")
        if not all(_looks_like_doi(doi) for doi in self.source_dois):
            raise ValueError("manuscript evidence source_dois must look like DOI strings")

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["artifact_path"] = project_relative_path(self.artifact_path)
        return payload


@dataclass(frozen=True)
class ModuleValidationPanel:
    """Finite validation status for one module's methods surface."""

    module: str
    checks: tuple[ResearchValidationRecord, ...]

    def __post_init__(self) -> None:
        if not self.module:
            raise ValueError("validation panel module must be nonempty")
        if not self.checks:
            raise ValueError("validation panel checks must not be empty")

    @property
    def validation_count(self) -> int:
        return len(self.checks)

    @property
    def passed_count(self) -> int:
        return sum(check.passed for check in self.checks)

    @property
    def validation_fraction(self) -> float:
        return float(self.passed_count / self.validation_count)

    @property
    def failed_checks(self) -> tuple[str, ...]:
        return tuple(check.name for check in self.checks if not check.passed)

    def as_dict(self) -> dict[str, object]:
        return {
            "module": self.module,
            "validation_count": self.validation_count,
            "passed_count": self.passed_count,
            "validation_fraction": self.validation_fraction,
            "failed_checks": self.failed_checks,
            "checks": [check.as_dict() for check in self.checks],
        }


@dataclass(frozen=True)
class ModuleVisualizationPanel:
    """Visualization coverage and provenance for one module."""

    module: str
    artifact_paths: tuple[str, ...]
    backends: tuple[str, ...]
    fidelity_levels: tuple[str, ...]
    validation_statuses: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.module:
            raise ValueError("visualization panel module must be nonempty")
        lengths = {
            len(self.artifact_paths),
            len(self.backends),
            len(self.fidelity_levels),
            len(self.validation_statuses),
        }
        if len(lengths) != 1:
            raise ValueError("visualization panel fields must have matching lengths")
        if not self.artifact_paths:
            raise ValueError("visualization panel artifact_paths must not be empty")
        for values in (
            self.artifact_paths,
            self.backends,
            self.fidelity_levels,
            self.validation_statuses,
        ):
            if not all(isinstance(value, str) and value for value in values):
                raise ValueError("visualization panel values must be nonempty strings")

    @property
    def artifact_count(self) -> int:
        return len(self.artifact_paths)

    @property
    def figure_count(self) -> int:
        return sum(_path_is_figure(path) for path in self.artifact_paths)

    @property
    def animation_count(self) -> int:
        return sum(path.endswith(".gif") for path in self.artifact_paths)

    def as_dict(self) -> dict[str, object]:
        return {
            "module": self.module,
            "artifact_count": self.artifact_count,
            "figure_count": self.figure_count,
            "animation_count": self.animation_count,
            "artifact_paths": tuple(project_relative_path(path) for path in self.artifact_paths),
            "backends": self.backends,
            "fidelity_levels": self.fidelity_levels,
            "validation_statuses": self.validation_statuses,
        }


@dataclass(frozen=True)
class ModuleMethodsPanel:
    """Module methods panel tying metrics, validation, visuals, and claims."""

    module: str
    fidelity_level: str
    primary_methods: tuple[str, ...]
    quantitative_metrics: dict[str, float]
    validation_panel: ModuleValidationPanel
    visualization_panel: ModuleVisualizationPanel
    manuscript_evidence: tuple[ManuscriptEvidenceLink, ...]
    known_gaps: tuple[str, ...]
    interpretation: str

    def __post_init__(self) -> None:
        if not self.module:
            raise ValueError("methods panel module must be nonempty")
        if not self.fidelity_level:
            raise ValueError("methods panel fidelity_level must be nonempty")
        if not self.primary_methods:
            raise ValueError("methods panel primary_methods must not be empty")
        _validate_metric_map(self.quantitative_metrics, self.module)
        if self.validation_panel.module != self.module:
            raise ValueError("validation panel module mismatch")
        if self.visualization_panel.module != self.module:
            raise ValueError("visualization panel module mismatch")
        if not self.manuscript_evidence:
            raise ValueError("methods panel manuscript_evidence must not be empty")
        if not self.known_gaps:
            raise ValueError("methods panel known_gaps must not be empty")
        if not self.interpretation:
            raise ValueError("methods panel interpretation must be nonempty")

    def as_dict(self) -> dict[str, object]:
        return {
            "module": self.module,
            "fidelity_level": self.fidelity_level,
            "primary_methods": self.primary_methods,
            "quantitative_metrics": self.quantitative_metrics,
            "validation_panel": self.validation_panel.as_dict(),
            "visualization_panel": self.visualization_panel.as_dict(),
            "manuscript_evidence": [link.as_dict() for link in self.manuscript_evidence],
            "known_gaps": self.known_gaps,
            "interpretation": self.interpretation,
        }


@dataclass(frozen=True)
class ScenarioSweepPanel:
    """Compact interpretation of one deterministic scenario/sensitivity sweep."""

    parameter: str
    values: tuple[float, ...]
    output_ranges: dict[str, float]
    dominant_output: str
    monotonic_outputs: tuple[str, ...]
    interpretation: str
    insensitive_outputs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.parameter:
            raise ValueError("scenario sweep parameter must be nonempty")
        if len(self.values) < 2:
            raise ValueError("scenario sweep values need at least two entries")
        _validate_numeric_sequence(self.values, f"{self.parameter} values")
        _validate_metric_map(self.output_ranges, f"{self.parameter} ranges")
        if not self.dominant_output:
            raise ValueError("scenario sweep dominant_output must be nonempty")
        if self.dominant_output not in self.output_ranges:
            raise ValueError("scenario sweep dominant_output must exist in ranges")
        if not self.interpretation:
            raise ValueError("scenario sweep interpretation must be nonempty")
        if not all(output in self.output_ranges for output in self.insensitive_outputs):
            raise ValueError("scenario sweep insensitive_outputs must exist in ranges")

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class MethodsAnalysisReport:
    """Science-first methods-analysis payload for BeeStack."""

    title: str
    summary: str
    module_panels: tuple[ModuleMethodsPanel, ...]
    scenario_sweeps: tuple[ScenarioSweepPanel, ...]
    manuscript_evidence_links: tuple[ManuscriptEvidenceLink, ...]
    top_validation_gaps: tuple[str, ...]
    figure_paths: tuple[str, ...]
    interactive_paths: tuple[str, ...]
    all_validations_passed: bool

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("methods report title must be nonempty")
        if not self.summary:
            raise ValueError("methods report summary must be nonempty")
        if not self.module_panels:
            raise ValueError("methods report needs module panels")
        if not self.scenario_sweeps:
            raise ValueError("methods report needs scenario sweeps")
        if not self.manuscript_evidence_links:
            raise ValueError("methods report needs manuscript evidence links")
        if not self.top_validation_gaps:
            raise ValueError("methods report top_validation_gaps must not be empty")
        for path in self.figure_paths + self.interactive_paths:
            if not path:
                raise ValueError("methods report artifact paths must be nonempty")

    @property
    def overall_validation_fraction(self) -> float:
        return float(
            np.mean([panel.validation_panel.validation_fraction for panel in self.module_panels])
        )

    @property
    def module_count(self) -> int:
        return len(self.module_panels)

    @property
    def visualization_count(self) -> int:
        return sum(panel.visualization_panel.artifact_count for panel in self.module_panels)

    def with_artifacts(
        self,
        figure_paths: tuple[str, ...],
        interactive_paths: tuple[str, ...],
    ) -> MethodsAnalysisReport:
        return MethodsAnalysisReport(
            title=self.title,
            summary=self.summary,
            module_panels=self.module_panels,
            scenario_sweeps=self.scenario_sweeps,
            manuscript_evidence_links=self.manuscript_evidence_links,
            top_validation_gaps=self.top_validation_gaps,
            figure_paths=figure_paths,
            interactive_paths=interactive_paths,
            all_validations_passed=self.all_validations_passed,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "summary": self.summary,
            "module_count": self.module_count,
            "overall_validation_fraction": self.overall_validation_fraction,
            "visualization_count": self.visualization_count,
            "all_validations_passed": self.all_validations_passed,
            "module_panels": [panel.as_dict() for panel in self.module_panels],
            "scenario_sweeps": [sweep.as_dict() for sweep in self.scenario_sweeps],
            "manuscript_evidence_links": [
                link.as_dict() for link in self.manuscript_evidence_links
            ],
            "source_claim_crosswalk": self.source_claim_crosswalk,
            "evidence_availability_counts": self.evidence_availability_counts,
            "top_validation_gaps": self.top_validation_gaps,
            "figure_paths": tuple(project_relative_path(path) for path in self.figure_paths),
            "interactive_paths": tuple(
                project_relative_path(path) for path in self.interactive_paths
            ),
        }

    @property
    def evidence_availability_counts(self) -> dict[str, int]:
        return {
            status: sum(
                link.availability_status == status for link in self.manuscript_evidence_links
            )
            for status in sorted(EVIDENCE_AVAILABILITY_STATES)
        }

    @property
    def source_claim_crosswalk(self) -> tuple[dict[str, object], ...]:
        panels = {panel.module: panel for panel in self.module_panels}
        rows: list[dict[str, object]] = []
        for link in self.manuscript_evidence_links:
            panel = panels.get(link.module)
            narrative = figure_narrative_for_path(link.artifact_path)
            rows.append(
                {
                    "module": link.module,
                    "method": "; ".join(panel.primary_methods) if panel else link.evidence_type,
                    "config_knobs": link.variable_tokens,
                    "artifact_path": project_relative_path(link.artifact_path),
                    "artifact_kind": link.artifact_kind,
                    "claim_tier": link.claim_tier,
                    "manuscript_section": link.manuscript_section,
                    "citation_keys": link.citation_keys,
                    "source_dois": link.source_dois,
                    "availability_status": link.availability_status,
                    "claim": link.claim,
                    "figure_caption": narrative.caption if narrative else link.claim,
                    "figure_alt_text": narrative.alt_text if narrative else link.claim,
                    "unsupported_inference": (
                        narrative.unsupported_inference
                        if narrative
                        else "Does not support claims beyond the linked generated artifact."
                    ),
                }
            )
        return tuple(rows)
