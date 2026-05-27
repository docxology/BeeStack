"""Write and enforce the BeeStack security posture audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack import audit_security_posture, finalize_project_outputs, security_posture_markdown


def main() -> None:
    audit = audit_security_posture(PROJECT_ROOT)
    reports_dir = PROJECT_ROOT / "output" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "security_posture_audit.json").write_text(
        json.dumps(audit.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (reports_dir / "security_posture_audit.md").write_text(
        security_posture_markdown(audit),
        encoding="utf-8",
    )
    finalize_project_outputs(PROJECT_ROOT)
    if not audit.passed:
        raise SystemExit("BeeStack security posture audit failed")
    print("BeeStack security posture audit passed")


if __name__ == "__main__":
    main()
