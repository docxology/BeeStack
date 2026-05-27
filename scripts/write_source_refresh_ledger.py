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

from beestack import finalize_project_outputs
from beestack.source_refresh import (
    external_dataset_registry,
    source_refresh_markdown,
    source_refresh_payload,
)
from beestack.utils import write_json


def main() -> None:
    out_dir = PROJECT_ROOT / "output" / "llm"
    data_dir = PROJECT_ROOT / "output" / "data"
    json_path = out_dir / "source_refresh_ledger.json"
    md_path = out_dir / "source_refresh_ledger.md"
    registry_path = data_dir / "external_dataset_registry.json"
    payload = source_refresh_payload(PROJECT_ROOT)
    write_json(json_path, payload, project_root=PROJECT_ROOT)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(source_refresh_markdown(PROJECT_ROOT), encoding="utf-8")
    write_json(
        registry_path,
        {
            "schema": "beestack.external_dataset_registry.v1",
            "records": [row.as_dict() for row in external_dataset_registry()],
        },
        project_root=PROJECT_ROOT,
    )
    finalize_project_outputs(PROJECT_ROOT)
    print(f"Wrote {json_path}, {md_path}, and {registry_path}")


if __name__ == "__main__":
    main()
