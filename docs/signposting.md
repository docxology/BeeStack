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
`.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `.uv-cache`, `htmlcov`,
`__pycache__`, and `*.egg-info`. Output-producing scripts call it after
successful writes so regenerated artifacts keep their local signposts.

Project-local support directories that are not caches still get explicit
guidance. For example, `.mplconfig/` is documented as Matplotlib render support,
not as scientific source data. Ignored export leaves such as `output/pdf/`,
`output/slides/`, and `output/web/` keep tracked signposts while their generated
payloads remain local.

## Readiness Report

`scripts/signpost_project_tree.py` also writes
`output/reports/project_readiness_review.md` and
`output/reports/project_readiness_review.json`. The report combines strict
signposting coverage, documentation-audit health, research-suite known gaps,
and a prioritized improvement backlog.

## Audit Gate

`uv run python scripts/audit_documentation.py` scans the top-level docs,
manuscript source, `output/reports/` docs, and every existing folder-level
`README.md`/`AGENTS.md`. It fails if any non-cache directory lacks either
signpost file, if a referenced generated output path is missing, or if hydrated
manuscript files contain unresolved variables.
