#!/usr/bin/env python3
"""Thin orchestrator: publication readiness gate for BeeStack release 1.0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from beestack.publication_readiness import check_publication_readiness


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit BeeStack publication readiness")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Project root (default: parent of scripts/)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when blockers remain",
    )
    parser.add_argument(
        "--require-doi",
        action="store_true",
        help="Treat empty publication.doi as a blocker",
    )
    args = parser.parse_args()

    result = check_publication_readiness(
        args.project_root,
        require_doi=args.require_doi,
    )
    reports_dir = args.project_root / "output" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "publication_readiness.json"
    report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if args.check and not result["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
