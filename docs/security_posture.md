# BeeStack security posture

BeeStack is an **offline research CLI** and manuscript pipeline. It is not a
network service, multi-tenant product, or production decision-support system.
Security work therefore concentrates on **supply-chain integrity**, **curated
network fetch**, **archive safety**, and **honest governance boundaries** rather
than perimeter hardening for internet-facing APIs.

## Threat model

The repository-local threat model lives at [`BeeStack-threat-model.md`](../BeeStack-threat-model.md).
Regenerate the posture audit after changing fetch policy, dataset registry URLs,
or security documentation:

```bash
uv run python scripts/run_security_audit.py
```

## Runtime boundaries

| Surface | Location | Control |
| --- | --- | --- |
| HTTPS empirical fetch | `src/beestack/brain/empirical_fetch.py` | Host allowlist via `validate_download_url`; post-redirect re-validation (TM-002) |
| Archive ingest | `src/beestack/brain/empirical_ingest.py`, `src/beestack/brain/anatomy.py` | Zip-slip rejection (`assert_safe_zip_member`); member-count and uncompressed-size caps (`validate_zip_archive_bounds`, TM-003) |
| Config load | `scripts/analysis_pipeline.py` | `yaml.safe_load` only |
| Domain logic | `src/beestack/` | No network I/O; presentation adapters write figures under `output/` |

Allowed download hosts (suffix match):

- `datadryad.org`
- `figshare.com` / `ndownloader.figshare.com`
- `bcp.fu-berlin.de` (Virtual Honeybee Standard Brain assets)

## Orchestration gates

The core analysis orchestrator writes a security posture report alongside
documentation and integrity audits:

```bash
uv run python scripts/analysis_pipeline.py
uv run python scripts/run_security_audit.py
uv run python scripts/audit_documentation.py
```

`output/reports/security_posture_audit.json` records registry URL validation,
forbidden-pattern scans (`shell=True`, unsafe `yaml.load`, `pickle.loads`,
`eval(`), and confirmation that only `empirical_fetch` performs urllib fetches.

## Nation-state / supply-chain posture (research context)

BeeStack follows template-repo practices inherited from the parent workspace:

- **`uv lock`** pins dependency versions; posture audit requires `uv.lock` present.
- **No secrets in git** — empirical credentials are not required; Dryad/Figshare
  assets used here are public.
- **Reproducible outputs** — `output/` is disposable; provenance is carried in
  JSON sidecars and manuscript variable hydration, not opaque checkpoints.
- **Conservative dual-use framing** — dance/pheromone kernels are reduced
  baselines; see [@sec:ethics] in the manuscript.

For deployment beyond a single-researcher workstation, treat the FlyBody/MuJoCo
toolchain, optional GPU stack, and any future hive sensor adapters as separate
trust zones with their own hardening (see threat model TM-006..TM-008).

## Related documentation

- [`AGENTS.md`](../AGENTS.md) — agent editing contract and verification commands
- [`docs/research_operations_playbook.md`](research_operations_playbook.md) — claim and provenance audit
- [`docs/digital_twin_path.md`](digital_twin_path.md) — governance readiness axis
- [`docs/manuscript/16_ethics_governance.md`](../manuscript/16_ethics_governance.md) — ethics and software-security prose
