# Project Signposting

BeeStack keeps a `README.md` and `AGENTS.md` in every non-cache project
directory, including generated output leaves such as FlyBody copied assets,
strict-scene body plans, empirical dataset folders, and diagnostic probe
folders. The goal is simple: every future researcher or agent can tell whether
a directory is canonical source, generated output, downloaded data, or
diagnostic scratch without guessing.

## Regeneration

```bash
uv run python scripts/signpost_project_tree.py
uv run python scripts/signpost_project_tree.py --check
```

The script excludes only cache/build directories: `.git`, `.venv`,
`.pytest_cache`, `.ruff_cache`, `htmlcov`, `__pycache__`, and `*.egg-info`.
Output-producing scripts call it after successful writes so regenerated
artifacts keep their local signposts.

## Readiness Report

`scripts/signpost_project_tree.py` also writes
`output/reports/project_readiness_review.md` and
`output/reports/project_readiness_review.json`. The report combines strict
signposting coverage, documentation-audit health, research-suite known gaps,
and a prioritized improvement backlog.

## Audit Gate

`uv run python scripts/audit_documentation.py` fails if any non-cache directory
lacks either signpost file, if a referenced generated output path is missing,
or if hydrated manuscript files contain unresolved variables.
