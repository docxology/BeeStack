#!/usr/bin/env python3
"""CLI for project-wide README/AGENTS signposts and readiness reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from beestack.documentation_signpost import (  # noqa: E402
    finalize_project_outputs,
    signposting_check_payload,
    write_signposts,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--check", action="store_true", help="Check coverage without writing.")
    parser.add_argument("--overwrite", action="store_true", help="Rewrite existing signposts.")
    args = parser.parse_args()

    if args.check:
        payload = signposting_check_payload(args.project_root)
        print(json.dumps(payload, indent=2, sort_keys=True))
        if not payload["passed"]:
            raise SystemExit("BeeStack signposting check failed")
        return
    result = write_signposts(args.project_root, overwrite=args.overwrite)
    finalize_project_outputs(args.project_root, overwrite_signposts=False)
    print(json.dumps(result.as_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
