"""Write the BeeStack external-source refresh ledger."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
SCRIPT_ROOT = PROJECT_ROOT / "scripts"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from beestack.source_refresh import write_source_refresh_ledger
from signpost_project_tree import write_project_readiness_review, write_signposts


def main() -> None:
    json_path, md_path = write_source_refresh_ledger(PROJECT_ROOT)
    write_signposts(PROJECT_ROOT)
    write_project_readiness_review(PROJECT_ROOT)
    print(f"Wrote {json_path} and {md_path}")


if __name__ == "__main__":
    main()
