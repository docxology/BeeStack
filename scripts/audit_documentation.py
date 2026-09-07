"""Write BeeStack documentation audit reports."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from beestack import audit_documentation, documentation_audit_markdown, finalize_project_outputs


def main() -> None:
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
    finalize_project_outputs(PROJECT_ROOT)
    if not audit.passed:
        raise SystemExit("BeeStack documentation audit failed")
    print("BeeStack documentation audit passed")


if __name__ == "__main__":
    main()
