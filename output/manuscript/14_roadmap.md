# Roadmap {#sec:roadmap}

The implementation roadmap follows the fidelity gaps exposed by the
research suite and the readiness review. It is ordered by
*scientific leverage per unit effort* rather than by module index: a
small improvement in BeeBrain empirical coverage can unlock multiple
downstream interpretations, while BeeBody calibration first strengthens
the Body evidence tier and then propagates through the existing
cross-layer contracts.

## Full digital-twin target

The long-horizon target is a systems-biology digital twin that spans a
single managed colony and a population of interacting colonies, using the
closed-loop, observation-updated sense of digital twin adopted in biomedical
systems work [@bjornsson2020digitaltwins]. BeeStack
is not there yet. The generated digital-twin readiness review currently
tracks 9 axes and reports mean maturity
0.244, with `population_twin_ready` resolved to
`False`. The top blocker is: Represent apiaries, feral colonies, queen/drone mating, migration, robbing/drifting, pathogen transmission, and landscape-mediated competition.
The next named artifact is `output/data/population_colony_network.json`.

That review reframes the roadmap around eight auditable scales:

1. molecular, omics, microbiome, pathogen, pesticide, and nutrition state;
2. tissue physiology, endocrine state, brood development, and mortality;
3. individual BeeBody biomechanics, sensory channels, and energetic cost;
4. neural dynamics, learning, navigation, and behaviour;
5. colony demography, resource stores, queen laying, disease, and task allocation;
6. nest microclimate, weather, land cover, floral phenology, and management events;
7. apiary and regional population networks, genetics, drift, robbing, migration,
   and pathogen transmission;
8. assimilation, uncertainty, forecast scoring, intervention counterfactuals,
   provenance, and governance.

The implementation rule is conservative: an axis moves from scaffold to
digital-twin evidence only when it has typed state variables, units,
source provenance, update equations or learned transition models,
longitudinal assimilation, held-out validation residuals, and a generated
artifact in `output/data/` or `output/reports/`.

Scholarship refresh hooks for those axes include: **axis 1** — BeeBiome
SRA metadata and pathogen-assay parsers [@rechlaval2025beebiome]; **axis 4**
— spatial/snRNA-seq validation tasks against reduced AL–MB–CX backends
[@naturecomm2025spatialbrain; @g3journal2023scrna]; **axis 6** — EPA hive
matrices, landscape pesticide exposure, and forage metabarcoding
[@epa2024hivematrices; @hisamoto2024landscape; @chege2025forage]; **axis 7**
— Auburn/AIA and COLOSS-style colony-loss surveys as assimilation targets
with held-out residuals [@auburn2025survey; @colossbeebook], not as v0
model outputs.

## 1. Build the colony-state ledger

Before adding more detailed submodels, BeeStack needs a conserving colony
ledger. This ledger should represent queen laying, eggs, larvae, pupae,
nurses, foragers, drones, dead adults, honey stores, pollen stores,
pathogen loads, pesticide burden, and management interventions as dated
state variables with units and provenance.

*Acceptance criterion:* a `colony_state_timeseries.json` artifact exists,
conserves individuals and resource stores under documented flows, and is
validated by a report comparing at least one held-out colony inspection or
BEEHAVE-compatible scenario.

## 2. Add driver ingestion and assimilation surfaces

A colony twin requires external drivers rather than internally chosen
scenario constants. Add parsers for weather, hive temperature/humidity,
hive weight, entrance counts, floral-resource proxies, management logs,
Varroa/pathogen assays, pesticide records, and apiary inspections. These
should feed a state-space assimilation layer with forecast skill and
posterior predictive checks.

*Acceptance criterion:* an `assimilation_posterior.nc` or interim JSON
posterior artifact is written, with a `forecast_skill.md` report describing
held-out residuals and uncertainty intervals.

## 3. Integrate the acquired BeeBrain calcium evidence

The Paoli MAT calcium archive [@paoli2024dryad] is now downloaded and
parsed into empirical response summaries, so acquisition and parsing are
complete and the modality is reported as parseable rather than
blocker-documented. The highest-leverage near-term move is to advance it
from a citation anchor to a model input: wire the parsed calcium
responses into the AL→MB encoding fidelity claim, expose them through the
empirical alignment metric in the integrated results, and raise the
calcium modality completeness beyond its current partial coverage in the
methods-analysis panel.

*Acceptance criterion:* the parsed calcium dataset feeds at least one
model-side AL→MB validation residual (not just a reporting panel), and
the calcium modality completeness recorded in
`output/data/brain_data_completeness.json` rises above its current
citation-anchor level.

## 4. Calibrate BeeBody beyond visual MJCF

Calibrate the real-FlyBody BeeBody path beyond the current visual MJCF
overlays. Specifically, calibrate against published honey-bee
biomechanics:

- segmental mass distribution and inertia tensors,
- adhesion at leg–comb and leg–floor surfaces,
- wing kinematics under varying load,
- leg contact mechanics at typical foraging gaits.

*Acceptance criterion:* a `body_calibration.json` artifact with cited
sources for each calibrated parameter and a methods-analysis Body
panel that reports the residual to the source data.

## 5. Replace BeeBrain kernels with simulator-backed dynamics

Replace the functional BeeBrain kernels with simulator-backed AL–MB–CX
dynamics — for example, a Brian2 or Nengo backend — and add validation
tasks for proboscis extension reflex (PER) conditioning, visual
learning, and navigation [@menzel2012honey; @stone2017central].

*Acceptance criterion:* a methods-analysis Brain panel that reports
quantitative residuals against at least one published bee
neuroscience task.

## 6. Extend BeeMind to a learned generative model

Extend BeeMind from bounded policy scoring to a fitted generative
model with learned transition and observation likelihoods. The
contract surface (`BeliefState`, `Action`) is already designed for
this swap; the work is in the inference machinery, not in the rest of
the stack [@friston2010free; @parr2017working].

*Acceptance criterion:* `BeeMind.score_policies()` substituted by a
learned variational posterior with diagnostic parity (same
diagnostic record fields, computed differently).

## 7. Scale BeeSwarm to BEEHAVE-compatible scenarios

Scale BeeSwarm beyond strict small-scene visualization by:

1. wiring the reduced communication summaries through a BEEHAVE
   adapter [@becher2014beehave] for full population-scale scenario
   comparisons;
2. later, training surrogate agents from higher-fidelity rollouts so
   that the 50-to-20,000 scale gap
   becomes a *learned* compression rather than a documented gap.

*Acceptance criterion:* a research-suite Swarm scorecard row that
reports both small-scene contact pairs and BEEHAVE-scale forager
counts, with traceable provenance for each.

## 8. Extend BeeNiche with ecology and demography

Calibrate BeeNiche seasonal forage witnesses, add brood demography, and
extend sparse 3D comb voxels while preserving the current adapter schemas
[@johnson2009self; @kronenberg1982colonial]. Live Hiveopolis runtime
coupling [@narsicht2020hiveopolis] is a longer-horizon target that
this step enables.

*Acceptance criterion:* a methods-analysis Niche panel that reports
source-calibrated seasonal-forage variance, brood-cohort survival, and a
parseable Hiveopolis adapter payload.

## 9. Keep project readiness automated

Keep project readiness automated: every generated output leaf should
remain signposted, audited, and regenerated by uv-managed commands.
This maintenance item preserves the evidentiary trail through every
other roadmap step.

*Acceptance criterion:* `SIGNPOSTED_DIRECTORY_COUNT` continues to
match the actual directory count, and the readiness review's
priority list continues to drive the next-iteration backlog.

## 10. Register external repository metadata

Materialize the scholarship refresh as durable registry artifacts:
`output/data/external_dataset_registry.json` plus ledger rows for BeeBiome,
HGD, BeeBDC, HAv3.1, survey portals, EPA hive matrices, and COLOSS BEEBOOK
(see [@sec:materials]).

*Acceptance criterion:* every registry row lists `wired_in_beestack: false`,
a target module, a blocker string, and an official DOI or HTTPS URL; the
documentation audit reports zero stale paths to the registry file.

## 11. Colony-health driver stubs

Add typed placeholder fields for Varroa load, viral titers, pesticide
burden, and microbiome summaries in the colony ledger schema—initialized to
zero or missing with explicit provenance until calibrated against field
data [@scientificreports2026amitraz; @wilfert2022dwv;
@glinski2024hivematrices].

*Acceptance criterion:* `colony_state_timeseries.json` (or successor artifact)
includes the stub fields with units and `source_provenance: null` until
assimilation populates them; no manuscript section claims non-zero values.

## 12. Waggle communication literature regression tests

Add regression checks that the Hadjitofi–Webb dance decoder and follower
orientation diagnostics remain consistent with published kinematic bounds
when run on registered Figshare deposits [@hadjitofi2024figshare;
@dong2023wagglesocial; @pnas2026waggleaudience].

*Acceptance criterion:* a methods-analysis or empirical test module reports
pass/fail against published summary statistics or tolerance bands documented
in `output/reports/waggle_literature_regression.json`.

## What is intentionally *not* in the roadmap

For clarity, the following are *not* roadmap items in v0:

- a colony-health decision-support API;
- a real-time hive sensor dashboard;
- a learned dance-language inverter beyond the
  Hadjitofi–Webb-anchored decoder [@hadjitofi2024figshare];
- a closed-source proprietary backend.

Those may become legitimate downstream projects; they are not
BeeStack's commitment.

## Releasing the roadmap

The roadmap is not a wish list. Each item has an acceptance criterion
expressed as a manuscript variable or methods-analysis panel. A
roadmap item is considered shipped when its acceptance criterion is
visible in the hydrated manuscript variables and in the corresponding
methods-analysis panel.
