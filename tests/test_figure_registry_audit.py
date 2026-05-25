from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

from beestack.figure_audit import audit_figures
from beestack.visualization.figure_metadata import write_figure_sidecar
from beestack.visualization.figure_registry import (
    figure_narrative_for_path,
    generic_figure_sidecar_fields,
    high_priority_figure_artifacts,
)
from beestack.visualization.style import MODULE_COLORS, module_color, style_context


def _varied_png(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(23)
    arr = (rng.random((32, 40, 3)) * 255).astype(np.uint8)
    Image.fromarray(arr, "RGB").save(path)
    return path


def test_style_helpers_expose_stable_module_colors() -> None:
    assert set(MODULE_COLORS) >= {"BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"}
    assert module_color("BeeBrain") == MODULE_COLORS["BeeBrain"]
    assert module_color("UnknownModule").startswith("#")
    with style_context():
        # The context manager should be usable by plotting code without leaking
        # implementation details into each figure builder.
        assert module_color("BeeBody") == MODULE_COLORS["BeeBody"]


def test_figure_narrative_registry_has_curated_primary_contract() -> None:
    narrative = figure_narrative_for_path(Path("output/figures/beestack_graphical_abstract.png"))

    assert narrative is not None
    assert narrative.manuscript_section == "manuscript/04_evidence_typed_architecture.md"
    assert narrative.manuscript_label == "fig:beestack_graphical_abstract"
    assert narrative.priority == "primary"
    assert "not" in narrative.unsupported_inference.lower()
    assert "caption" in narrative.as_sidecar_fields()
    assert "rougier2014figures" in narrative.design_citation_keys
    assert "cleveland1984graphical" in narrative.design_citation_keys
    assert "ragan2016provenance" in narrative.design_citation_keys
    assert "output/figures/beestack_graphical_abstract.png" in high_priority_figure_artifacts()
    assert "output/figures/manuscript_figure_claim_map.png" in high_priority_figure_artifacts()
    for artifact in (
        "output/figures/beestack_scholarship_evidence_matrix.png",
        "output/figures/beebody_beeswarm_micro_macro_calibration.png",
        "output/figures/beebrain_beemind_anatomy_policy_map.png",
        "output/figures/beeniche_adapter_niche_map.png",
        "output/figures/beestack_validation_readiness_residuals.png",
    ):
        figure = figure_narrative_for_path(artifact)
        assert figure is not None, artifact
        assert figure.priority == "primary"
        assert figure.citation_keys
        assert figure.source_dois
        assert "Does not" in figure.unsupported_inference
        assert artifact in high_priority_figure_artifacts()


def test_all_inserted_manuscript_figures_have_curated_registry_narratives() -> None:
    project_root = Path(__file__).resolve().parents[1]
    image_re = re.compile(r"!\[[^\]]+\]\((?P<path>[^)]+)\)\{#(?P<label>[^}]+)\}")
    references: list[tuple[str, str]] = []
    for markdown_path in sorted((project_root / "output" / "manuscript").glob("*.md")):
        for match in image_re.finditer(markdown_path.read_text(encoding="utf-8")):
            resolved = (markdown_path.parent / match.group("path")).resolve()
            artifact = resolved.relative_to(project_root.resolve()).as_posix()
            references.append((artifact, match.group("label")))

    assert references
    for artifact, label in references:
        narrative = figure_narrative_for_path(artifact)
        assert narrative is not None, artifact
        assert narrative.priority == "primary", artifact
        assert narrative.manuscript_label == label


def test_generic_figure_fields_do_not_promise_animation_sidecars() -> None:
    fields = generic_figure_sidecar_fields(
        Path("output/animations/beebody.gif"),
        title="BeeBody animation",
        fidelity="real_flybody_3d",
        source_data="animation manifest",
        regeneration_command="uv run python scripts/generate_animations.py",
    )

    assert fields["artifact_kind"] == "animation"
    assert "sidecar" not in str(fields["caption"])
    assert "manifest" in str(fields["caption"])


def test_write_figure_sidecar_adds_registry_narrative_metadata(tmp_path: Path) -> None:
    fig = _varied_png(tmp_path / "beestack_graphical_abstract.png")

    sidecar = write_figure_sidecar(
        fig,
        title="BeeStack graphical abstract",
        backend="Matplotlib",
        fidelity="architecture schematic",
        source_data="output/data/run_summary.json",
        validation_status="nonblank",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
    )

    payload = json.loads(sidecar.read_text(encoding="utf-8"))
    assert payload["caption"].startswith("Showcase architecture schematic")
    assert payload["alt_text"]
    assert payload["manuscript_section"] == "manuscript/04_evidence_typed_architecture.md"
    assert payload["manuscript_label"] == "fig:beestack_graphical_abstract"
    assert payload["claim_tier"] == "architecture_schematic"
    assert payload["design_citation_keys"]
    assert payload["accessibility_checks"]["normal_text_passed"]
    assert payload["unsupported_inference"]
    assert payload["priority"] == "primary"


def test_figure_audit_detects_path_label_sidecar_and_primary_failures(tmp_path: Path) -> None:
    manuscript = tmp_path / "output" / "manuscript"
    figures = tmp_path / "output" / "figures"
    manuscript.mkdir(parents=True)
    _varied_png(figures / "present.png")
    _varied_png(figures / "primary.png")
    (figures / "primary.json").write_text("{}", encoding="utf-8")
    (manuscript / "01.md").write_text(
        "\n".join(
            (
                "![Present figure](../figures/present.png){#fig:dup}",
                "![Missing figure](../figures/missing.png){#fig:dup}",
                "![Primary figure](../figures/primary.png){#fig:primary}",
                "![Absent evidence supports validation](../figures/primary.png){#fig:absent}",
            )
        ),
        encoding="utf-8",
    )

    audit = audit_figures(
        tmp_path,
        required_primary_artifacts=("output/figures/primary.png", "output/figures/absent.png"),
        absent_artifacts=("output/figures/primary.png",),
    )

    assert not audit.passed
    assert "output/manuscript/01.md:../figures/missing.png" in audit.missing_image_paths
    assert "fig:dup" in audit.duplicate_labels
    assert "output/figures/present.json" in audit.missing_sidecar_paths
    assert audit.missing_high_priority_artifacts == ("output/figures/absent.png",)
    assert audit.absent_positive_claims


def test_figure_audit_detects_sidecar_mismatch_and_absolute_path_leakage(
    tmp_path: Path,
) -> None:
    manuscript = tmp_path / "output" / "manuscript"
    figures = tmp_path / "output" / "figures"
    manuscript.mkdir(parents=True)
    figure_path = _varied_png(figures / "registered.png")
    (figures / "registered.json").write_text(
        json.dumps(
            {
                "figure_path": str(figure_path),
                "title": "Registered",
                "backend": "Matplotlib",
                "fidelity": "diagnostic",
                "source_data": "test fixture",
                "validation_status": "nonblank",
                "regeneration_command": "uv run python scripts/analysis_pipeline.py",
                "caption": "Different caption.",
                "alt_text": "Alt text.",
                "manuscript_section": "manuscript/01.md",
                "manuscript_label": "fig:sidecar-label",
                "claim_tier": "diagnostic",
                "unsupported_inference": "Does not support external claims.",
                "artifact_kind": "figure",
            }
        ),
        encoding="utf-8",
    )
    (manuscript / "01.md").write_text(
        "![Manuscript caption](../figures/registered.png){#fig:markdown-label}\n",
        encoding="utf-8",
    )

    audit = audit_figures(
        tmp_path,
        required_primary_artifacts=("output/figures/registered.png",),
    )

    assert not audit.passed
    assert "output/figures/registered.json:figure_path" in audit.absolute_path_leaks
    assert "output/figures/registered.json:manuscript_label" in audit.sidecar_manuscript_mismatches
    assert "output/figures/registered.json:caption" in audit.sidecar_manuscript_mismatches


def test_figure_audit_detects_missing_sidecar_narrative_fields(tmp_path: Path) -> None:
    manuscript = tmp_path / "output" / "manuscript"
    figures = tmp_path / "output" / "figures"
    manuscript.mkdir(parents=True)
    _varied_png(figures / "incomplete.png")
    (figures / "incomplete.json").write_text(
        json.dumps(
            {
                "figure_path": "output/figures/incomplete.png",
                "title": "Incomplete",
                "backend": "Matplotlib",
            }
        ),
        encoding="utf-8",
    )
    (manuscript / "01.md").write_text(
        "![Incomplete](../figures/incomplete.png){#fig:incomplete}\n",
        encoding="utf-8",
    )

    audit = audit_figures(
        tmp_path,
        required_primary_artifacts=("output/figures/incomplete.png",),
    )

    assert not audit.passed
    assert "output/figures/incomplete.json:caption" in audit.sidecar_required_field_failures
    assert "output/figures/incomplete.json:artifact_kind" in audit.sidecar_required_field_failures


def test_figure_audit_detects_primary_caption_contract_failures(tmp_path: Path) -> None:
    manuscript = tmp_path / "output" / "manuscript"
    figures = tmp_path / "output" / "figures"
    manuscript.mkdir(parents=True)
    _varied_png(figures / "primary.png")
    (figures / "primary.json").write_text(
        json.dumps(
            {
                "figure_path": "output/figures/primary.png",
                "title": "Primary",
                "backend": "Matplotlib",
                "fidelity": "diagnostic",
                "source_data": "output/data/run_summary.json",
                "validation_status": "nonblank",
                "regeneration_command": "uv run python scripts/analysis_pipeline.py",
                "caption": "Primary generated figure.",
                "alt_text": "Primary figure.",
                "manuscript_section": "manuscript/01.md",
                "manuscript_label": "fig:primary",
                "claim_tier": "diagnostic",
                "unsupported_inference": "Does not support external claims.",
                "artifact_kind": "figure",
                "priority": "primary",
            }
        ),
        encoding="utf-8",
    )
    (manuscript / "01.md").write_text(
        "![Primary generated figure.](../figures/primary.png){#fig:primary}\n",
        encoding="utf-8",
    )

    audit = audit_figures(
        tmp_path,
        required_primary_artifacts=("output/figures/primary.png",),
    )

    assert not audit.passed
    assert "output/figures/primary.json:caption_contract" in (
        audit.primary_caption_contract_failures
    )


def test_figure_audit_accepts_compound_backend_caption_contract(tmp_path: Path) -> None:
    manuscript = tmp_path / "output" / "manuscript"
    figures = tmp_path / "output" / "figures"
    manuscript.mkdir(parents=True)
    _varied_png(figures / "primary.png")
    (figures / "primary.json").write_text(
        json.dumps(
            {
                "figure_path": "output/figures/primary.png",
                "title": "Primary",
                "backend": "Matplotlib empirical-data renderer",
                "fidelity": "diagnostic",
                "source_data": "output/data/run_summary.json",
                "validation_status": "nonblank",
                "regeneration_command": "uv run python scripts/analysis_pipeline.py",
                "caption": "Empirical diagnostic.",
                "alt_text": "Primary figure.",
                "manuscript_section": "manuscript/01.md",
                "manuscript_label": "fig:primary",
                "claim_tier": "diagnostic",
                "unsupported_inference": "Does not support external claims.",
                "artifact_kind": "figure",
                "priority": "primary",
            }
        ),
        encoding="utf-8",
    )
    (manuscript / "01.md").write_text(
        (
            "![Matplotlib empirical diagnostic generated from output data; "
            "sidecar validation checks the raster, and the figure supports "
            "availability review rather than external validation.]"
            "(../figures/primary.png){#fig:primary}\n"
        ),
        encoding="utf-8",
    )

    audit = audit_figures(
        tmp_path,
        required_primary_artifacts=("output/figures/primary.png",),
    )

    assert not audit.primary_caption_contract_failures
