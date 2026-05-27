# Materials and Source Provenance {#sec:materials}

BeeStack treats scholarship, software, generated reports, and empirical
availability records as materials. The source-refresh ledger under
`output/llm/source_refresh_ledger.json` records the current public-source
refresh: each row carries a citation key, DOI or official source URL,
direct-verification status, claim tier, availability state, manuscript
targets, and figure targets. Perplexity/web research is allowed only as a
discovery channel. A source can influence manuscript claims only after it
enters the offline ledger with direct DOI or official-source verification.

[@fig:scholarship_evidence_matrix] links scholarship anchors to verification status and manuscript targets; see also [@sec:materials].

![Matplotlib beestack scholarship evidence matrix shows Scholarship evidence matrix mapping directly verified sources to manuscript sections, figure targets, DOI-bearing source records, and claim tiers. Generated from source refresh ledger, bibliography, source audit, and figure registry. Sidecar validation checks raster, source routing, and registered claim tier. Does not replace direct DOI/source verification or add empirical data.](../figures/beestack_scholarship_evidence_matrix.png){#fig:scholarship_evidence_matrix}

## Source tiers

The project separates three source tiers. **Scholarship anchors** support
background, related-work, and governance language. **Method anchors**
support architecture or methods design choices, such as FlyBody/MuJoCo
body rendering, BEEHAVE-compatible colony summaries, waggle flight-path
and robot-dance context, or antennal-lobe and brain-atlas mappings.
**Validation anchors** support how the manuscript distinguishes software
verification from biological validation, uncertainty, residuals, and
closed-loop digital-twin readiness [@oreskes1994verification;
@fair4rs2022principles; @bjornsson2020digitaltwins].

This tiering is intentionally conservative. FAIR and FAIR4RS materials
govern software provenance, metadata, licensing, and reuse
[@wilkinson2016fair; @lamprecht2020fairsoftware;
@fair4rs2022principles]. They do not make a biological claim stronger.
Waggle-dance, neuroethology, and robotic-dance sources support
mechanistic context and interface design [@riley2005flightpaths;
@landgraf2011roboticdance; @hateren2019neuroethology]. They do not turn
the reduced recruitment kernel into a colony-calibrated model.

## Empirical availability

Empirical BeeBrain analysis remains data-gated. Public or licensed
payloads are first recorded as metadata, then only downloaded and parsed
when the source is legally reusable, tractable, and has an inspectable
schema. Paywalled, too-large, absent, or underspecified payloads remain
availability records with explicit blockers. The manuscript never fills
those gaps with synthetic calcium traces, invented waggle tracks, or
fabricated colony histories.

The same rule applies to BeeSwarm and BeeNiche adapters. BEEHAVE is a
valid method anchor for colony-summary compatibility [@becher2014beehave],
but BeeStack does not report BEEHAVE-scale validation unless scenario
tables, demographic traces, or external validation residuals are actually
wired into the generated reports. Hiveopolis and robotic-waggle sources
can motivate interface boundaries, not real-time hive-control claims,
until the project has public controller logs, closed-loop safety records,
and governance artifacts.

## External repository landscape (not yet wired)

BeeStack maintains a machine-readable registry at
`output/data/external_dataset_registry.json` alongside the source-refresh ledger.
The table below lists community repositories and survey portals identified in
the scholarship refresh as high-leverage **future** provenance targets. Every
row remains outside the empirical BeeBrain fetch contract until registered,
downloaded under license, parsed, and audited.

| Resource | Type | Official ID | BeeStack module target | Status |
| --- | --- | --- | --- | --- |
| BeeBiome portal [@rechlaval2025beebiome] | microbiome SRA index | DOI `10.1186/s12859-025-06229-7` | BeeNiche / colony ledger | metadata only |
| HGD / HymenopteraMine [@walsh2022hgd] | genomics annotation | DOI `10.1093/nar/gkab1018` | BeeBrain annotation | not registered |
| BeeBDC [@dorey2023beebdc] | global occurrence | DOI `10.1038/s41597-023-02626-w` | BeeNiche forage / landscape | not registered |
| NCBI HAv3.1 [@wallberg2019hav31] | reference genome | DOI `10.1186/s12864-019-5639-3` | BeeBrain / omics join | not registered |
| Auburn / AIA survey [@auburn2025survey] | colony-loss survey | [official portal](https://apiaryinspectors.org/US-beekeeping-survey-24-25) | colony ledger / assimilation | survey not ingested |
| USDA NASS honey statistics | production time series | [NASS honey portal](https://esmis.nal.usda.gov/publication/honey) | colony ledger | no parser |
| EPA hive-matrix residues [@epa2024hivematrices] | pesticide concentrations | DOI `10.23719/1523343` | BeeNiche drivers | not registered |
| COLOSS BEEBOOK [@colossbeebook] | standard methods manual | [coloss.org/beebook](https://coloss.org/activities/beebook/) | methods / validation | not mapped chapter-wise |

[@fig:scholarship_evidence_matrix] maps directly verified scholarship anchors
from `output/llm/source_refresh_ledger.json`; the external registry records
repository-level targets that remain unwired in v0.

## Generated materials

Generated materials are produced by scripts rather than hand-edited after
the fact. Figure sidecars preserve caption, alt text, manuscript section,
label, claim tier, fidelity tier, source data, regeneration command,
citation keys, source DOIs, and unsupported-inference language. Hydrated
manuscript sections may reference only generated images that exist and
pass the figure audit. Project-local artifact paths serialize as stable
`output/...` paths so reports can move between checkouts without leaking
absolute filesystem locations.

## Claim routing

Every current-facing claim routes to one of four surfaces: manuscript
source with Pandoc citations, a generated JSON or Markdown report, a
figure sidecar, or an explicit known-gap record. If a claim cannot be
routed to one of those surfaces, it stays in the roadmap or limitations
sections. This routing keeps the source-refresh ledger, bibliography,
figure registry, documentation audit, and hydrated manuscript aligned.

## Software supply-chain materials

Python dependencies are pinned in `uv.lock` at the project root. The
security posture gate (`output/reports/security_posture_audit.json`) records
whether the threat model, operations doc, lockfile, curated download
allowlist, and forbidden-pattern scans pass before release. Empirical fetch
uses HTTPS host allowlisting in `beestack.security`; archive ingest rejects
zip-slip members. These controls are documented in `BeeStack-threat-model.md`,
`docs/security_posture.md`, and [@sec:ethics]. They govern **software
integrity**, not biological validation.
