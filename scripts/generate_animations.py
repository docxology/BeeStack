"""Generate module-level BeeStack animations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack import BeeStackConfig, config_from_mapping, finalize_project_outputs
from beestack.utils import project_relative_path, project_relative_payload
from beestack.visualization import generate_module_animations, waggle_dance_visualization_config
from beestack.visualization.animation_manifest import (
    bee_signatures,
    build_animation_manifest_payload,
    contact_physics_markdown,
)
from beestack.visualization.bee_signature import bee_render_report_markdown
from beestack.visualization.render_stills import publish_flybody_render_stills


def load_config() -> BeeStackConfig:
    config_path = PROJECT_ROOT / "manuscript" / "config.yaml"
    if not config_path.exists():
        return BeeStackConfig()
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    return config_from_mapping(payload.get("beestack", payload))


def main() -> None:
    cfg = load_config()
    artifacts = generate_module_animations(cfg, PROJECT_ROOT / "output" / "animations")
    manifest, bee_visual_report_payload, contact_physics_report_payload = (
        build_animation_manifest_payload(
            artifacts,
            cfg,
            project_root=PROJECT_ROOT,
            extended_contact_metrics=True,
        )
    )
    waggle_config = waggle_dance_visualization_config(cfg)
    manifest = project_relative_payload(manifest, PROJECT_ROOT)
    path = PROJECT_ROOT / "output" / "data" / "animation_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (PROJECT_ROOT / "output" / "data" / "waggle_dance_visualization_config.json").write_text(
        json.dumps(waggle_config.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_dir = PROJECT_ROOT / "output" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "bee_visual_verification.json").write_text(
        json.dumps(bee_visual_report_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    signatures = bee_signatures(artifacts, cfg, project_root=PROJECT_ROOT)
    (report_dir / "bee_visual_verification.md").write_text(
        (
            "\n".join(
                bee_render_report_markdown(
                    signature,
                    project_relative_path(artifact.path, PROJECT_ROOT),
                    project_relative_path(artifact.source, PROJECT_ROOT),
                )
                for artifact, signature in signatures
            )
            + "\n\n"
            + contact_physics_markdown(
                contact_physics_report_payload,
                extended_metrics=True,
            )
        ),
        encoding="utf-8",
    )
    (report_dir / "flybody_contact_physics.json").write_text(
        json.dumps(contact_physics_report_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (report_dir / "flybody_contact_physics.md").write_text(
        contact_physics_markdown(
            contact_physics_report_payload,
            extended_metrics=True,
        ),
        encoding="utf-8",
    )
    published = publish_flybody_render_stills(PROJECT_ROOT)
    if published:
        print(f"Published {len(published)} FlyBody render still(s) to output/figures/renders/")
    finalize_project_outputs(PROJECT_ROOT)
    if not bee_visual_report_payload["bee_like"]:
        raise RuntimeError("BeeBody visual verification failed")
    if not contact_physics_report_payload["passed"]:
        raise RuntimeError("FlyBody BeeSwarm contact-physics verification failed")
    print(f"Generated {len(artifacts)} BeeStack animations")


if __name__ == "__main__":
    main()
