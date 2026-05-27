#!/usr/bin/env python3
"""Download curated BeeBrain empirical datasets from Dryad, Figshare, and anatomy URLs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from beestack.brain.empirical_fetch import fetch_empirical_sources
from beestack.documentation_signpost import finalize_project_outputs


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Download curated BeeBrain empirical datasets from Dryad, Figshare, and anatomy URLs."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root / "output" / "data" / "empirical_sources",
        help="Directory for catalog and downloaded archives.",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Write catalog JSON only; do not download archives.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download archives even when cached files exist.",
    )
    args = parser.parse_args()
    summary = fetch_empirical_sources(
        args.output_dir,
        metadata_only=args.metadata_only,
        force=args.force,
    )
    print(
        f"Cataloged {summary.catalog_count} files; "
        f"downloaded {summary.downloaded_archives} archives, "
        f"{summary.downloaded_files} files, "
        f"{summary.downloaded_anatomy} anatomy assets."
    )
    finalize_project_outputs(project_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
