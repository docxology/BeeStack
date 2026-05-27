# BeeStack security module

Offline security helpers for curated empirical fetch and repository posture
audits. Not a network daemon or authentication layer.

## Modules

| Module | Role |
| --- | --- |
| `url_policy.py` | HTTPS host allowlist for `empirical_fetch` |
| `path_safety.py` | Zip-slip and path traversal guards |
| `posture.py` | Static posture audit and Markdown report |

## Commands

```bash
uv run python scripts/run_security_audit.py
uv run pytest tests/test_security_posture.py -v
```

See [`docs/security_posture.md`](../../docs/security_posture.md) and
[`BeeStack-threat-model.md`](../../BeeStack-threat-model.md).
