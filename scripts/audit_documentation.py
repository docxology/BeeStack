"""Write BeeStack documentation audit reports."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack import audit_documentation, documentation_audit_markdown
from signpost_project_tree import write_project_readiness_review, write_signposts


def main() -> None:
    write_signposts(PROJECT_ROOT)
    write_project_readiness_review(PROJECT_ROOT)
    audit = audit_documentation(PROJECT_ROOT)
    report_dir = PROJECT_ROOT / "output" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "documentation_audit.json").write_text(
        json.dumps(audit.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (report_dir / "documentation_audit.md").write_text(
        documentation_audit_markdown(audit),
        encoding="utf-8",
    )
    write_project_readiness_review(PROJECT_ROOT)
    if not audit.passed:
        raise SystemExit("BeeStack documentation audit failed")
    print("BeeStack documentation audit passed")


if __name__ == "__main__":
    main()
