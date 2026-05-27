"""Verify rendered BeeBody and strict BeeSwarm FlyBody/MuJoCo outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack.documentation_signpost import finalize_project_outputs
from beestack.visualization.bee_render_verification import run_bee_render_verification


def main() -> int:
    result = run_bee_render_verification(PROJECT_ROOT)
    report_dir = PROJECT_ROOT / "output" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "bee_visual_verification.json").write_text(
        json.dumps(result["report"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (report_dir / "bee_visual_verification.md").write_text(result["markdown"], encoding="utf-8")
    if not result["passed"]:
        raise SystemExit("BeeBody/BeeSwarm visual verification failed")
    scores = ", ".join(
        f"{mode}={signature.score:.3f}/silhouette={signature.silhouette_score:.3f}"
        for mode, _, _, signature in result["signatures"]
    )
    swarm_report = result["report"]["swarm"]
    print(
        f"BeeBody visual verification passed: {scores}; swarm scenes={swarm_report['scene_count']}"
    )
    finalize_project_outputs(PROJECT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
