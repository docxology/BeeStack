# BeeNiche Methods: Comb, Heat, and Adapter Schemas {#sec:methods_niche}

BeeNiche models the *constructed environment* of the colony. It owns a
comb grid with 864 voxels (default $18 \times 12 \times 4$),
content fields (brood, food, wax, empty), a thermal field, a foraging
landscape summary, and adapter-style outputs intended to stay
compatible with future BEEHAVE [@becher2014beehave] and Hiveopolis
[@hiveopolis2019project] runtime coupling.

## Comb construction

The comb kernel maintains a four-channel content field over the comb
voxel grid. Wax deposition updates local comb occupancy, neighborhood
density, and content metrics. The dimensionless wax deposition threshold
(`wax_deposit_threshold`) is a synthetic model setting, not a value
established by a verified comb-construction source: below the threshold, no new
cell is produced; above it, neighborhood-coordinated deposition raises
local occupancy. The kernel records the final comb occupancy fraction
(0.083 at the end of the integrated run) and the
mean over the rollout so that comb growth is auditable as a time series
rather than only as an endpoint.

## Reduced brood thermal field

Thermal stepping updates brood-temperature error and supports
fanning/heat-source witnesses. The brood-target band is
$[32, 36]$ °C centred at 34 °C
[@kronenberg1982colonial], and the kernel reports the
brood-temperature error
2.875 °C from that target at the end of
the run, plus the mean over the rollout. Heat sources (active bees
clustered around brood) and heat sinks (foragers returning from cool
ambient) are represented as bounded scalars applied at configured grid
locations. The kernel is not an aerodynamic CFD solver; it is a
*measurable thermoregulation witness*.
The configured reduced kernel applies a bounded thermoregulation gain of
0.240 on occupied comb cells. Generated
methods/research scorecards compare its brood-temperature error against a
configured target; meeting that target is not biological thermal calibration.

## Standalone foraging-landscape summaries

Landscape helpers summarize patch value, distance, nectar quality,
seasonal forage amplitude, weather penalties, and competition pressure
without an external weather or nectar engine. Patch distances are model
attributes in kilometers; waggle-dance foraging studies motivate this surface
without calibrating its distribution [@couvillon2014waggle].
These standalone summaries are not connected to the current Body/Brain
observation channel or to recruitment-driven depletion. The integrated driver
advances its reduced niche thermal state independently.

## Planned driver and forage data surfaces

The reduced BeeNiche baseline uses deterministic seasonal/weather witnesses rather than
external observations. The scholarship refresh identifies adapter targets
that should enter only through typed driver ingestion (see [@sec:roadmap]
step 2): EPA and peer-reviewed hive-matrix pesticide residues
[@glinski2024hivematrices; @epa2024hivematrices; @hisamoto2024landscape],
land-use effects on forage nutrition [@landuse2024nutrition], DNA
metabarcoding of forage plants [@chege2025forage], and global occurrence
aggregates such as BeeBDC [@dorey2023beebdc]. BeeNet-style national
monitoring programmes and USDA production statistics are listed in
`output/data/external_dataset_registry.json` as unwired metadata. None
of these sources validate the current comb or thermal kernel until
parsers, licenses, and held-out residuals are recorded in generated reports.

## Declared niche interfaces and currently absent feedback

`stack_contracts` declares niche-to-body thermal/surface context and a
swarm-to-niche field interface. The current `step_simulation` does not execute
those feedback routes. It advances the comb temperature using fixed heat/fanning
inputs, then records comb metrics independently of the Body/Brain update.
Grid geometry and temperature are not passed into `step_body` or
`process_observation`; Body thermosensation comes from Body state. Swarm task
pressures do not drive the thermal update, and stored agents are not retasked.
Closing these feedback routes requires explicit state transfer, unit and timing
contracts, and appropriate validation; merely increasing grid size would not
provide that evidence.

## BEEHAVE and Hiveopolis compatibility schemas

BeeNiche emits adapter-compatible payloads for BEEHAVE
[@becher2014beehave] (colony-level forager, brood, and food-store
summaries) and Hiveopolis [@hiveopolis2019project] (sensor-stream
abstractions over the comb grid). The adapter shape is not load-bearing
in the current run — no downstream BEEHAVE or Hiveopolis runtime is
invoked — but the schema is preserved so that coupling can happen
without breaking BeeStack's internal contracts.

[@fig:niche_adapter_map] maps BeeNiche adapter schemas to niche and external-engine anchors.

![Final comb fraction and maximum absolute thermal error from supplied reduced records, beside conceptual NicheAdapterSummary field groups. No adapter payload is supplied to this figure. Generated from source refresh ledger, niche methods records, simulation records, and adapter notes using Matplotlib. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not validate full ecology, real-time hive control, or thermodynamic colony dynamics.](../figures/beeniche_adapter_niche_map.png){#fig:niche_adapter_map}

## Comb and thermal methods panel

The methods-analysis Niche panel tracks final and mean comb fraction,
final and mean brood-temperature error, brood-target margin within the
configured band, comb-voxel count (864), and forage-radius
midpoint. The panel is written to
`output/figures/methods/beeniche_methods_comb_thermal.png` so niche
claims are anchored to *quantitative traces* rather than to prose alone.

[@fig:niche_methods_comb_thermal] plots comb occupancy and brood-thermal diagnostics.

![BeeNiche methods panel showing comb occupancy, brood thermal error, foraging-radius context, and configured niche-kernel self-tests. Generated from MethodsAnalysisReport and simulation records using Matplotlib/pandas. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not support a full ecology or hive thermodynamics engine.](../figures/methods/beeniche_methods_comb_thermal.png){#fig:niche_methods_comb_thermal}

## Ecology and runtime-coupling gaps

BeeNiche is a *voxel comb and thermal kernel with adapter schemas*. It
now includes deterministic seasonal/weather forage witnesses, but it
does not currently model:

- brood demography (egg-to-emergence aging within voxels),
- 3D pollen storage with depletion kinetics, or
- live Hiveopolis or BEEHAVE runtime callbacks.

Each of those is a roadmap item. The architectural commitment is
that adding any of them should *only* modify BeeNiche internals; the
cross-layer `CombGrid` and `PheromoneField` contracts that link
BeeNiche to BeeSwarm and BeeBody do not change.
