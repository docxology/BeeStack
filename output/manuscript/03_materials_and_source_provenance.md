# Materials and Source Provenance

BeeStack treats scholarship, software, generated reports, and empirical
availability records as materials. The source-refresh ledger under
`output/llm/source_refresh_ledger.json` records the current public-source
refresh: each row carries a citation key, DOI or official source URL,
direct-verification status, claim tier, availability state, manuscript
targets, and figure targets. Perplexity/web research is allowed only as a
discovery channel. A source can influence manuscript claims only after it
enters the offline ledger with direct DOI or official-source verification.

![Matplotlib source-refresh matrix generated from the verified ledger, source audit, bibliography, and figure registry; sidecar validation checks the raster, and the figure records manuscript/figure routing rather than adding empirical data.](../figures/beestack_scholarship_evidence_matrix.png){#fig:scholarship_evidence_matrix}

## Source Tiers

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

## Empirical Availability

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

## Generated Materials

Generated materials are produced by scripts rather than hand-edited after
the fact. Figure sidecars preserve caption, alt text, manuscript section,
label, claim tier, fidelity tier, source data, regeneration command,
citation keys, source DOIs, and unsupported-inference language. Hydrated
manuscript sections may reference only generated images that exist and
pass the figure audit. Project-local artifact paths serialize as stable
`output/...` paths so reports can move between checkouts without leaking
absolute filesystem locations.

## Claim Routing

Every current-facing claim routes to one of four surfaces: manuscript
source with Pandoc citations, a generated JSON or Markdown report, a
figure sidecar, or an explicit known-gap record. If a claim cannot be
routed to one of those surfaces, it stays in the roadmap or limitations
sections. This routing keeps the source-refresh ledger, bibliography,
figure registry, documentation audit, and hydrated manuscript aligned.
