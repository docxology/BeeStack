"""Write and enforce the BeeStack generated-report semantic audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack import audit_generated_reports, generated_report_audit_markdown


def main() -> None:
    reports_dir = PROJECT_ROOT / "output" / "reports"
    audit = audit_generated_reports(PROJECT_ROOT)
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "generated_report_audit.json").write_text(
        json.dumps(audit.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (reports_dir / "generated_report_audit.md").write_text(
        generated_report_audit_markdown(audit),
        encoding="utf-8",
    )
    if not audit.passed:
        raise SystemExit("BeeStack generated-report audit failed")
    print("BeeStack generated-report audit passed")


if __name__ == "__main__":
    main()
