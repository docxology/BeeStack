"""Write and enforce the BeeStack generated-report semantic audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack import (
    audit_generated_reports,
    audit_security_posture,
    generated_report_audit_markdown,
)
from beestack.publication_readiness import check_publication_readiness


def main() -> None:
    reports_dir = PROJECT_ROOT / "output" / "reports"
    security_audit = audit_security_posture(PROJECT_ROOT)
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
    if not security_audit.passed:
        raise SystemExit("BeeStack security posture audit failed")
    publication = check_publication_readiness(PROJECT_ROOT)
    (reports_dir / "publication_readiness.json").write_text(
        json.dumps(publication, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not publication["ok"]:
        blockers = publication.get("blockers", ())
        raise SystemExit(
            "BeeStack publication readiness failed: "
            + "; ".join(str(item) for item in blockers)
        )
    print("BeeStack generated-report audit passed")
    print("BeeStack security posture audit passed")
    print("BeeStack publication readiness passed")
    for warning in publication.get("warnings", ()):
        print(f"publication warning: {warning}")


if __name__ == "__main__":
    main()
