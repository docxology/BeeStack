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
| HTTPS empirical fetch | `src/beestack/brain/empirical_fetch.py` | Every redirect hop is validated before dispatch; exact-origin Dryad credentials never cross origins; OAuth redirects refuse |
| Container ingest | `src/beestack/brain/empirical_parsers/`, `anatomy.py` | Path rejection plus shared ZIP-tree, XLSX logical-cell, MATLAB/HDF5 graph/array budgets before expansion |
| Config load | `scripts/analysis_pipeline.py` | `yaml.safe_load` only |
| Domain logic | `src/beestack/` | Computation has no network I/O; explicit acquisition and presentation adapters perform bounded side effects |

Curated HTTPS authorities include Dryad, Figshare, the registered FU Berlin
atlas and MDPI supplementary resources. Storage redirects use exact reviewed
Dryad/Figshare S3 host/path rules, not generic AWS or arbitrary Lambda endpoints.
No registered Dryad Lambda authority was observed; unregistered endpoints refuse.

Payloads publish atomically only after completion/size checks, with a verified
`<filename>.complete.json` size/SHA-256 marker and a hash binding the original
locator, source DOI/version and advertised size. Query values are significant to
that identity but are not stored in the marker. Nonempty legacy/unbound caches
remain unverified and eligible for reacquisition. Failed refreshes preserve old
bytes without crediting them to a new source. Approximate atlas catalog sizes are
identity metadata, not exact transfer-integrity requirements. Refused URL errors
and acquisition catalog fields do not echo credentials or query secrets.
Malformed provider locators are catalogued as per-file failures rather than aborting
metadata-only acquisition and suppressing successful peer observations.

Default budgets: metadata 8 MB, file 2 GB, fetch operation 12 GB; archive trees
8 levels/5,000 entries/5 GB expanded; XLSX 512 MB input/256 MB package/128 MB
member and 100,000 rows/4,096 columns/5 million cells per sheet/10 million total;
array materialization 4 GB, graph depth 16 and 10,000 nodes. These are logical
admission limits, not a measured peak-RSS guarantee or proof every upstream
payload fits. Policy rejection is explicit, never an empty successful parse.
HDF5 external/soft links, unsupported variable/reference/compound dtypes and
cycles refuse. VRML consumers read only the bounded prefix they actually use.

Parsers read archive members; they do not extract filesystem links or files.
The reviewed threat is hostile-data/resource exhaustion, not an invented ZIP
filesystem-write exploit. Native library defects and dependency authenticity
remain separate risks; the static posture audit is not a runtime penetration test.

Current-analysis markers additionally bind raw payloads, the active configuration
and implementation bytes; replacing/deleting a payload or changing analysis code
invalidates current evidence. These hashes detect change, not publisher authenticity
or scientific validity. A parsed statistical supplement does not establish neural
connectivity, held-out residuals or calibrated colony behavior.

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
- **No secrets in git** — optional Dryad credentials belong in environment variables,
  never source/config/output. They are scoped only to the authorized Dryad origin.
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
- [`docs/manuscript/16_ethics_governance.md`](manuscript/16_ethics_governance.md) — ethics and software-security prose
