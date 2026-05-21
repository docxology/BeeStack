# .github/workflows

Keep workflow steps conservative and aligned with local commands. Do not add
network-heavy full empirical downloads to routine CI; use metadata-only fetches,
assemble-only report generation after prerequisite scripts, digital-twin
readiness checks, and generated-report audits.

- Canonical source: This directory's files are source-of-truth unless local guidance says otherwise.
- Regeneration command: n/a
