# BeeStack security posture audit

Status: **passed**

## Checks

- Threat model present: `True`
- Security operations doc present: `True`
- uv.lock present (supply-chain pin): `True`
- Registry URL violations: `0`
- Forbidden pattern hits: `0`
- urllib modules under `src/`: `beestack/brain/empirical_fetch.py`

## Operational notes

BeeStack is an offline research CLI. Network fetch is confined to
`beestack.brain.empirical_fetch` with HTTPS host allowlisting.
See `docs/security_posture.md` and `BeeStack-threat-model.md`.
