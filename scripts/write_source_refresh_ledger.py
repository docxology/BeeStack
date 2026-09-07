"""Write the BeeStack external-source refresh ledger."""

from __future__ import annotations

from pathlib import Path

from beestack.documentation_signpost import finalize_project_outputs
from beestack.pipeline import write_source_refresh_ledger_outputs

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    json_path, md_path, registry_path = write_source_refresh_ledger_outputs(PROJECT_ROOT)
    finalize_project_outputs(PROJECT_ROOT)
    print(f"Wrote {json_path}, {md_path}, and {registry_path}")


if __name__ == "__main__":
    main()
