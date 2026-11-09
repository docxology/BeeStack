"""Behavioral negative controls for production publication and figure admission."""

import json
import shutil
from pathlib import Path

import pytest
import yaml

from beestack.figure_audit import audit_figures, manuscript_image_references
from beestack.publication_readiness import check_publication_readiness
from beestack.version import MANUSCRIPT_VERSION, PACKAGE_VERSION

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def generated_manuscript(tmp_path: Path) -> Path:
    output = tmp_path / "output"
    output.mkdir()
    shutil.copytree(PROJECT_ROOT / "output/figures", output / "figures")
    shutil.copytree(PROJECT_ROOT / "output/manuscript", output / "manuscript")
    return tmp_path


@pytest.mark.parametrize("doi", ["not-a-doi", "10.5281/zenodo.20420557"])
def test_strict_deposit_rejects_malformed_or_known_wrong_version_doi(
    tmp_path: Path, doi: str
) -> None:
    canonical = tmp_path / "docs/manuscript"
    canonical.mkdir(parents=True)
    (canonical / "config.yaml").write_text(
        yaml.safe_dump({"paper": {"version": MANUSCRIPT_VERSION}, "publication": {"doi": doi}})
    )
    (tmp_path / "pyproject.toml").write_text(f'[project]\nversion = "{PACKAGE_VERSION}"\n')
    result = check_publication_readiness(tmp_path, require_doi=True)
    assert result["checks"]["doi_configured"]
    assert any("publication.doi" in blocker for blocker in result["blockers"])


def test_default_manuscript_audit_rejects_extra_indexed_diagnostic(
    generated_manuscript: Path,
) -> None:
    tmp_path = generated_manuscript
    output = tmp_path / "output"
    assert audit_figures(tmp_path).passed
    artifact = "output/figures/beemind_policy_timeline.png"
    sidecar = (tmp_path / artifact).with_suffix(".json")
    metadata = json.loads(sidecar.read_text())
    assert metadata["priority"] == "indexed"
    section = output / "manuscript/00_abstract.md"
    with section.open("a") as handle:
        handle.write(
            "\n![" + metadata["caption"] + "](../figures/beemind_policy_timeline.png)"
            "{#fig:extra_indexed_diagnostic}\n"
        )
    result = audit_figures(tmp_path)
    assert not result.passed
    assert artifact in result.uncurated_reference_paths


def test_registered_artifact_cannot_bypass_caption_contract_as_indexed(
    generated_manuscript: Path,
) -> None:
    assert audit_figures(generated_manuscript).passed
    reference = manuscript_image_references(generated_manuscript)[0]
    sidecar = reference.resolved_path.with_suffix(".json")
    metadata = json.loads(sidecar.read_text())
    metadata.update(
        priority="indexed", caption="Unrelated diagnostic caption", manuscript_label="fig:wrong"
    )
    sidecar.write_text(json.dumps(metadata))
    result = audit_figures(generated_manuscript)
    assert not result.passed
    assert any(issue.endswith(":caption") for issue in result.sidecar_manuscript_mismatches)
    assert any(
        issue.endswith(":manuscript_label") for issue in result.sidecar_manuscript_mismatches
    )
