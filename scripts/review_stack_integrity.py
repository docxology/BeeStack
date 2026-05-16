"""Write the BeeStack cross-layer integrity review reports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack import (
    BeeStackConfig,
    config_from_mapping,
    integrity_review_markdown,
    stack_integrity_review,
)


def load_config() -> BeeStackConfig:
    config_path = PROJECT_ROOT / "manuscript" / "config.yaml"
    if not config_path.exists():
        return BeeStackConfig()
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    return config_from_mapping(payload.get("beestack", payload))


def main() -> None:
    cfg = load_config()
    review = stack_integrity_review(cfg)
    report_dir = PROJECT_ROOT / "output" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "beestack_integrity_review.json").write_text(
        json.dumps(review.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (report_dir / "beestack_integrity_review.md").write_text(
        integrity_review_markdown(review),
        encoding="utf-8",
    )
    if not review.all_checks_passed:
        raise SystemExit("BeeStack integrity review failed")
    print("BeeStack integrity review passed")


if __name__ == "__main__":
    main()
