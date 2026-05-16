"""Write BeeStack digital-twin readiness reports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack.digital_twin import assess_digital_twin_readiness, digital_twin_readiness_markdown


def main() -> None:
    """Assess the full digital-twin target and write JSON/Markdown artifacts."""

    review = assess_digital_twin_readiness()
    data_dir = PROJECT_ROOT / "output" / "data"
    reports_dir = PROJECT_ROOT / "output" / "reports"
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "digital_twin_readiness.json").write_text(
        json.dumps(review.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (reports_dir / "digital_twin_readiness.md").write_text(
        digital_twin_readiness_markdown(review),
        encoding="utf-8",
    )
    print(
        "BeeStack digital-twin readiness written: "
        f"mean_maturity={review.mean_maturity:.3f}, axes={len(review.axes)}"
    )


if __name__ == "__main__":
    main()
