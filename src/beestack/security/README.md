# BeeStack security module

Offline security helpers for curated empirical fetch and repository posture
audits. Not a network daemon or authentication layer.

## Modules

| Module | Role |
| --- | --- |
| `url_policy.py` | HTTPS host allowlist for `empirical_fetch` |
| `path_safety.py` | Read-only archive path guards, shared tree budgets, completed-cache evidence |
| `posture.py` | Static posture audit and Markdown report |

## Intake contract

The fetcher uses one redirect handler for metadata, OAuth and file transfers.
Every resolved hop must pass HTTPS/curated-host validation before dispatch;
cross-origin credentials are stripped and OAuth redirects are rejected. Storage
access is restricted to registered Dryad/Figshare buckets, not arbitrary AWS or
Lambda authorities. Unregistered Lambda endpoints are rejected.

Transport caps are 8 MB metadata, 2 GB per file and 12 GB per fetch operation.
Files publish through a sibling temporary file only after exact Content-Length
completion (when supplied), with a `<file>.complete.json` size/SHA-256 marker
binding the original locator, source DOI/version and advertised size. Byte-only
or unbound legacy receipts remain retryable; failed refreshes preserve old bytes
without crediting them to a new source. Registry atlas sizes
are approximate, not exact integrity requirements. Completion and a local hash
do not establish upstream authenticity or scientific completeness.

`ArchiveBudget` bounds each recursive intake tree to depth 8, 5,000 entries
(including directories) and 5 GB expanded bytes; nested container bytes and
their expanded descendants both count. Irrelevant members are not expanded.
These are read-only parsers, not extraction or symlink-materialization APIs.
Resource-policy errors are explicit `IntakePolicyError` exceptions.


## Commands

```bash
uv run python scripts/run_security_audit.py
uv run pytest tests/test_security_posture.py -v
```

See [`docs/security_posture.md`](../../../docs/security_posture.md) and
[`BeeStack-threat-model.md`](../../../BeeStack-threat-model.md).
