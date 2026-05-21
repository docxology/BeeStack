"""Narrative registry for manuscript-facing BeeStack figures."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class FigureNarrative:
    """Manuscript-facing interpretation and provenance for one figure artifact."""

    artifact_path: str
    title: str
    caption: str
    alt_text: str
    manuscript_section: str
    manuscript_label: str
    claim_tier: str
    fidelity_level: str
    source_data: str
    regeneration_command: str
    unsupported_inference: str
    priority: str = "supporting"
    citation_keys: tuple[str, ...] = ()
    source_dois: tuple[str, ...] = ()
    design_citation_keys: tuple[str, ...] = ()
    design_source_dois: tuple[str, ...] = ()
    artifact_kind: str = "figure"

    def __post_init__(self) -> None:
        for field_name, value in asdict(self).items():
            if field_name in {
                "citation_keys",
                "source_dois",
                "design_citation_keys",
                "design_source_dois",
            }:
                if not all(isinstance(item, str) and item for item in value):
                    raise ValueError(f"figure narrative {field_name} values must be nonempty")
                continue
            if not isinstance(value, str) or not value:
                raise ValueError(f"figure narrative {field_name} must be nonempty")
        if self.priority not in {"primary", "supporting", "indexed"}:
            raise ValueError("figure narrative priority must be primary, supporting, or indexed")
        for doi in (*self.source_dois, *self.design_source_dois):
            doi_text = doi.removeprefix("https://doi.org/")
            if not (doi_text.startswith("10.") and "/" in doi_text):
                raise ValueError(f"figure narrative DOI is malformed: {doi}")

    def as_sidecar_fields(self) -> dict[str, object]:
        """Return fields that extend the JSON figure sidecar contract."""

        return {
            "caption": self.caption,
            "alt_text": self.alt_text,
            "manuscript_section": self.manuscript_section,
            "manuscript_label": self.manuscript_label,
            "claim_tier": self.claim_tier,
            "citation_keys": self.citation_keys,
            "source_dois": self.source_dois,
            "design_citation_keys": self.design_citation_keys,
            "design_source_dois": self.design_source_dois,
            "unsupported_inference": self.unsupported_inference,
            "priority": self.priority,
            "source_data": self.source_data,
            "artifact_kind": self.artifact_kind,
        }

    def as_index_fields(self) -> dict[str, object]:
        """Return fields used by the manuscript figure index."""

        return {
            "caption": self.caption,
            "alt_text": self.alt_text,
            "manuscript_label": self.manuscript_label,
            "claim_tier": self.claim_tier,
            "citation_keys": self.citation_keys,
            "source_dois": self.source_dois,
            "design_citation_keys": self.design_citation_keys,
            "design_source_dois": self.design_source_dois,
            "unsupported_inference": self.unsupported_inference,
            "priority": self.priority,
        }


_DEFAULT_CITATIONS = ("wilson2017good", "lamprecht2020fairsoftware")
_DEFAULT_DOIS = ("10.1371/journal.pcbi.1005510", "10.3233/DS-190026")
_DEFAULT_DESIGN_CITATIONS = (
    "rougier2014figures",
    "cleveland1984graphical",
    "crameri2020colour",
    "w3c2023wcag21",
    "wilkinson2016fair",
    "heer2012interactive",
    "ragan2016provenance",
)
_DEFAULT_DESIGN_DOIS = (
    "10.1371/journal.pcbi.1003833",
    "10.1080/01621459.1984.10478080",
    "10.1038/s41467-020-19160-7",
    "10.1038/sdata.2016.18",
    "10.1145/2133806.2133821",
    "10.1109/TVCG.2015.2467551",
)


def _narrative(
    artifact_path: str,
    *,
    title: str,
    caption: str,
    alt_text: str,
    manuscript_section: str,
    manuscript_label: str,
    claim_tier: str,
    fidelity_level: str,
    source_data: str,
    regeneration_command: str,
    unsupported_inference: str,
    priority: str = "supporting",
    citation_keys: tuple[str, ...] = _DEFAULT_CITATIONS,
    source_dois: tuple[str, ...] = _DEFAULT_DOIS,
    design_citation_keys: tuple[str, ...] = _DEFAULT_DESIGN_CITATIONS,
    design_source_dois: tuple[str, ...] = _DEFAULT_DESIGN_DOIS,
) -> FigureNarrative:
    return FigureNarrative(
        artifact_path=artifact_path,
        title=title,
        caption=caption,
        alt_text=alt_text,
        manuscript_section=manuscript_section,
        manuscript_label=manuscript_label,
        claim_tier=claim_tier,
        fidelity_level=fidelity_level,
        source_data=source_data,
        regeneration_command=regeneration_command,
        unsupported_inference=unsupported_inference,
        priority=priority,
        citation_keys=citation_keys,
        source_dois=source_dois,
        design_citation_keys=design_citation_keys,
        design_source_dois=design_source_dois,
    )


FIGURE_NARRATIVES: tuple[FigureNarrative, ...] = (
    _narrative(
        "output/figures/beestack_graphical_abstract.png",
        title="BeeStack graphical abstract",
        caption=(
            "Showcase architecture schematic linking BeeBody, BeeBrain, BeeMind, "
            "BeeSwarm, and BeeNiche through typed contracts and generated evidence."
        ),
        alt_text="Five BeeStack modules arranged as a left-to-right contract chain.",
        manuscript_section="manuscript/03_system_architecture.md",
        manuscript_label="fig:beestack_graphical_abstract",
        claim_tier="architecture_schematic",
        fidelity_level="architecture schematic",
        source_data="module coverage records and stack contract definitions",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not support a claim of biological or digital-twin validation.",
        priority="primary",
    ),
    _narrative(
        "output/figures/beestack_evidence_ladder.png",
        title="BeeStack evidence ladder",
        caption=(
            "Visual evidence contract separating backend, claim tier, validation "
            "status, source data, and unsupported inference for current BeeStack figures."
        ),
        alt_text="Tiered evidence ladder with current BeeStack capabilities and blocked claims.",
        manuscript_section="manuscript/09_visualization_and_validation.md",
        manuscript_label="fig:beestack_evidence_ladder",
        claim_tier="fidelity_boundary",
        fidelity_level="cross-stack evidence schematic",
        source_data="methods analysis, readiness review, and generated artifact manifests",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not remove the assimilation, residual, uncertainty, or governance gaps.",
        priority="primary",
    ),
    _narrative(
        "output/figures/manuscript_figure_claim_map.png",
        title="BeeStack manuscript figure claim map",
        caption=(
            "Manuscript figure claim map showing inserted primary figures by manuscript "
            "section, claim tier, source-data class, validation status, and conservative boundary."
        ),
        alt_text=(
            "Table-style map of manuscript figures with section placement, claim tier, "
            "source-data class, validation status, and not-supported boundaries."
        ),
        manuscript_section="manuscript/09_visualization_and_validation.md",
        manuscript_label="fig:manuscript_figure_claim_map",
        claim_tier="manuscript_figure_provenance_map",
        fidelity_level="manuscript evidence map",
        source_data="figure registry and manuscript figure index",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not add empirical evidence beyond the registered figure sidecars.",
        priority="primary",
    ),
    _narrative(
        "output/figures/methods/beebody_methods_telemetry_dashboard.png",
        title="BeeBody methods telemetry dashboard",
        caption=(
            "BeeBody methods dashboard showing reduced telemetry, energy, wing-power, "
            "and morphology cues beside the FlyBody-backed fidelity boundary."
        ),
        alt_text="Four-panel BeeBody telemetry dashboard with speed, wing power, energy, and cues.",
        manuscript_section="manuscript/04_body_methods.md",
        manuscript_label="fig:body_methods_dashboard",
        claim_tier="strict_visual_plus_reduced_telemetry",
        fidelity_level="FlyBody-backed render diagnostics plus reduced telemetry",
        source_data="MethodsAnalysisReport and simulation records",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not calibrate honeybee biomechanics or aerodynamics.",
        priority="primary",
        citation_keys=("vaxenburg2025flybody", "todorov2012mujoco"),
        source_dois=("10.1038/s41586-025-09029-4", "10.1109/IROS.2012.6386109"),
    ),
    _narrative(
        "output/figures/methods/beebrain_methods_empirical_completeness.png",
        title="BeeBrain empirical methods completeness",
        caption=(
            "BeeBrain completeness dashboard reporting available empirical channels, "
            "parser gaps, and the absence of locally parsed calcium datasets."
        ),
        alt_text="BeeBrain empirical completeness panel with source availability and gap markers.",
        manuscript_section="manuscript/05_brain_methods.md",
        manuscript_label="fig:brain_methods_completeness",
        claim_tier="empirical_reduced_or_availability_gated",
        fidelity_level="empirical completeness summary projected into reduced contracts",
        source_data="MethodsAnalysisReport and empirical analysis report",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not support connectome-scale or calcium-validated dynamics.",
        priority="primary",
        citation_keys=("galizia1999glomerular", "brandt2005standardbrain", "paoli2024dryad"),
        source_dois=("10.1038/8144", "10.1002/cne.20644", "10.5061/dryad.qbzkh18sc"),
    ),
    _narrative(
        "output/figures/methods/beemind_methods_policy_landscape.png",
        title="BeeMind policy landscape",
        caption=(
            "BeeMind policy landscape showing finite expected-free-energy terms, "
            "candidate-policy margin, and deterministic action-contract outputs."
        ),
        alt_text="BeeMind policy diagnostics with finite policy metrics and validation status.",
        manuscript_section="manuscript/06_mind_methods.md",
        manuscript_label="fig:mind_methods_policy",
        claim_tier="reduced_validated_kernel",
        fidelity_level="reduced deterministic active-inference diagnostic",
        source_data="MethodsAnalysisReport and policy-selection diagnostics",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not support a learned or biologically calibrated generative model.",
        priority="primary",
        citation_keys=("friston2010free", "parr2017working"),
        source_dois=("10.1038/nrn2787", "10.1038/s41598-017-15249-0"),
    ),
    _narrative(
        "output/figures/methods/beeswarm_methods_contact_recruitment.png",
        title="BeeSwarm contact and recruitment diagnostics",
        caption=(
            "BeeSwarm dashboard separating strict small-scene contact physics from "
            "reduced recruitment and BEEHAVE-compatible colony summaries."
        ),
        alt_text="BeeSwarm methods panel with contact metrics and reduced recruitment traces.",
        manuscript_section="manuscript/07_swarm_methods.md",
        manuscript_label="fig:swarm_methods_contact",
        claim_tier="strict_small_scene_not_colony_dynamics",
        fidelity_level="strict scene contact diagnostic with reduced-kernel context",
        source_data="MethodsAnalysisReport, animation manifest, and simulation records",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not validate colony-scale recruitment dynamics.",
        priority="primary",
        citation_keys=("todorov2012mujoco", "becher2014beehave", "hadjitofi2024currentbiology"),
        source_dois=(
            "10.1109/IROS.2012.6386109",
            "10.1111/1365-2664.12222",
            "10.1016/j.cub.2024.02.045",
        ),
    ),
    _narrative(
        "output/figures/methods/beeniche_methods_comb_thermal.png",
        title="BeeNiche comb and thermal diagnostics",
        caption=(
            "BeeNiche methods panel showing comb occupancy, brood thermal error, "
            "foraging-radius context, and deterministic niche-kernel validation."
        ),
        alt_text="BeeNiche methods panel with comb, thermal, and forage-context diagnostics.",
        manuscript_section="manuscript/08_niche_methods.md",
        manuscript_label="fig:niche_methods_comb_thermal",
        claim_tier="reduced_validated_kernel",
        fidelity_level="reduced deterministic niche diagnostic",
        source_data="MethodsAnalysisReport and simulation records",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not support a full ecology or hive thermodynamics engine.",
        priority="primary",
        citation_keys=("kronenberg1982colonial", "johnson2009self", "becher2014beehave"),
        source_dois=("10.1111/1365-2664.12222",),
    ),
    _narrative(
        "output/figures/empirical/brain_data_completeness_matrix.png",
        title="Brain data completeness matrix",
        caption=(
            "Empirical completeness matrix showing which BeeBrain source rows are "
            "registered, locally available, parseable, and source-verified."
        ),
        alt_text="Matrix of BeeBrain source availability, parser status, and verification state.",
        manuscript_section="manuscript/11_empirical_results.md",
        manuscript_label="fig:brain_data_completeness_matrix",
        claim_tier="empirical_availability_diagnostic",
        fidelity_level="empirical dataset availability diagnostic",
        source_data="output/data/brain_data_completeness.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not replace absent calcium payloads with synthetic traces.",
        priority="primary",
        citation_keys=("galizia1999glomerular", "brandt2005standardbrain", "paoli2024dryad"),
        source_dois=("10.1038/8144", "10.1002/cne.20644", "10.5061/dryad.qbzkh18sc"),
    ),
    _narrative(
        "output/figures/empirical/bee_brain_multimodal_source_map.png",
        title="BeeBrain multimodal source map",
        caption=(
            "Multimodal source map organizing anatomy, odor-response, antennal, "
            "and waggle-follower records by integration target and local availability."
        ),
        alt_text="Network-style map of empirical BeeBrain source channels and integration targets.",
        manuscript_section="manuscript/11_empirical_results.md",
        manuscript_label="fig:brain_multimodal_source_map",
        claim_tier="empirical_availability_diagnostic",
        fidelity_level="empirical dataset availability diagnostic",
        source_data="output/data/brain_data_completeness.json and empirical analysis report",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not support a complete multimodal empirical assimilation pipeline.",
        priority="primary",
        citation_keys=(
            "galizia1999glomerular",
            "brandt2005standardbrain",
            "hadjitofi2024currentbiology",
        ),
        source_dois=("10.1038/8144", "10.1002/cne.20644", "10.1016/j.cub.2024.02.045"),
    ),
    _narrative(
        "output/figures/research/stack_synthesis_dashboard.png",
        title="BeeStack cross-stack synthesis dashboard",
        caption=(
            "Cross-stack synthesis dashboard summarizing validation fractions, "
            "readiness, artifacts, explicit gaps, and scholarship anchors."
        ),
        alt_text="Four-panel synthesis dashboard with readiness bars, artifact-gap scatter, gates, and findings.",
        manuscript_section="manuscript/12_research_suite_results.md",
        manuscript_label="fig:stack_synthesis_dashboard",
        claim_tier="cross_stack_synthesis_diagnostic",
        fidelity_level="cross-stack synthesis diagnostic, not biological validation",
        source_data="output/reports/stack_synthesis_review.json",
        regeneration_command="uv run python scripts/run_research_suite.py",
        unsupported_inference="Does not make BeeStack digital-twin ready.",
        priority="primary",
    ),
)

_BY_ARTIFACT = {narrative.artifact_path: narrative for narrative in FIGURE_NARRATIVES}
_BY_NAME = {Path(narrative.artifact_path).name: narrative for narrative in FIGURE_NARRATIVES}


def all_figure_narratives() -> tuple[FigureNarrative, ...]:
    """Return registered manuscript-facing figure narratives."""

    return FIGURE_NARRATIVES


def high_priority_figure_artifacts() -> tuple[str, ...]:
    """Return artifacts that should appear in the hydrated manuscript."""

    return tuple(
        narrative.artifact_path
        for narrative in FIGURE_NARRATIVES
        if narrative.priority == "primary"
    )


def figure_narrative_for_path(path: Path | str) -> FigureNarrative | None:
    """Return a registered narrative for an artifact path or filename."""

    path_obj = Path(path)
    normalized = _normalize_artifact_path(path_obj)
    return _BY_ARTIFACT.get(normalized) or _BY_NAME.get(path_obj.name)


def generic_figure_sidecar_fields(
    path: Path,
    *,
    title: str,
    fidelity: str,
    source_data: str,
    regeneration_command: str,
) -> dict[str, object]:
    """Return conservative narrative metadata for non-curated generated figures."""

    human_title = title or path.stem.replace("_", " ").title()
    artifact_kind = "animation" if path.suffix.lower() == ".gif" else "figure"
    metadata_surface = (
        "manifest and manuscript-index validation metadata"
        if artifact_kind == "animation"
        else "sidecar validation metadata"
    )
    return {
        "caption": (
            f"{human_title} generated from {source_data}; this figure is a "
            f"{fidelity} and should be interpreted through its {metadata_surface}."
        ),
        "alt_text": f"{human_title} generated by BeeStack visualization tooling.",
        "manuscript_section": "output/reports/manuscript_figure_index.md",
        "manuscript_label": f"fig:{path.stem}",
        "claim_tier": "generated_diagnostic",
        "citation_keys": (),
        "source_dois": (),
        "unsupported_inference": (
            "Does not support claims beyond the generated artifact and stated fidelity tier."
        ),
        "priority": "indexed",
        "artifact_kind": artifact_kind,
        "source_data": source_data,
        "regeneration_command": regeneration_command,
    }


def _normalize_artifact_path(path: Path) -> str:
    parts = path.as_posix().split("/")
    if "output" in parts:
        return "/".join(parts[parts.index("output") :])
    return path.as_posix()
