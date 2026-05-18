# Ethics and Data Provenance

BeeStack ingests public data about a living organism, and runs that
data through a stack whose downstream applications could plausibly
include agriculture, ecology, robotics, and policy. The ethical
commitments below name those exposures and the project's response to
each.

## Data sources and licensing

Every empirical source registered in `src/beestack/research/methods.py`
is a public source, dataset, or publication with provenance metadata:
a DOI or source note where available, plus a license or access note
when the source provides one. The table below separates dataset
licenses from publication/atlas access notes.

| Source | DOI / source note | License / access note |
|--------|-------------------|-----------------------|
| Paoli AL calcium imaging [@paoli2024dryad] | 10.5061/dryad.qbzkh18sc | Dryad CC0 |
| Carcaud multisite GCaMP [@carcaud2022dryad] | 10.5061/dryad.83bk3j9tt | Dryad CC0 |
| Andreu alarm receptors [@andreu2025dryad] | 10.5061/dryad.rv15dv4k2 | Dryad CC0 |
| Jernigan antennal kinematics [@jernigan2026dryad] | 10.5061/dryad.qjq2bvqw6 | Dryad CC0 |
| Nouvian biogenic amines [@nouvian2017dryad] | 10.5061/dryad.rj10c | Dryad CC0 |
| Hadjitofi–Webb dance follower kinematics [@hadjitofi2024figshare] | 10.6084/m9.figshare.24715977.v1 | Figshare CC BY 4.0 |
| Honey-Bee Standard Brain ecosystem [@rybak2010digital] | — | Atlas, public |
| Galizia glomerular code [@galizia1999glomerular] | 10.1038/6406 | Nature Neuroscience |
| Szyszka Granger AL dynamics [@szyszka2023granger] | 10.3390/insects14060539 | MDPI open access |
| Kaneko Kenyon-cell subtypes [@kaneko2016kenyon] | 10.1186/s40851-016-0051-6 | Zoological Letters open access |

The download manifest under `output/data/empirical_sources/` records
the DOI, source URL, file size, and download timestamp for each local
payload. The Hadjitofi–Webb dataset's CC BY 4.0 license is honored by
explicit attribution in the methods analysis, in the manuscript
sections that use the data, and in the bibliography.

## Animal-research ethics

BeeStack does not generate new animal-research data. All empirical
inputs are derived from previously published, externally reviewed
work whose original ethical-review and approval procedures are the
responsibility of the source publications. The current pipeline
neither requires nor performs additional ethical review, because no
new live-animal experimentation is conducted.

Should a future BeeStack downstream project couple to a live monitored
hive (a possibility named in the BEEHAVE/Hiveopolis adapter roadmap work),
that downstream project will be subject to its host institution's
animal-research ethical review at that time. The current commitment
is therefore: *the architectural seam is in place, but the activation
is not*.

## Dual-use considerations

A future hive-coupled, whole-colony simulation scaffold would have
plausible dual-use exposure in three directions:

1. **Agricultural application.** A calibrated colony model could
   inform pesticide-exposure forecasting or pollination optimization.
   BeeStack does not currently support quantitative recommendations
   in either direction, and the limitations enumeration makes this
   explicit.
2. **Wildlife monitoring.** Sensor-stream coupling through the
   Hiveopolis adapter [@narsicht2020hiveopolis] could expose
   individually-monitored hives. The current code path emits adapter
   *schemas* only and does not exfiltrate any sensor data.
3. **Biosecurity.** Detailed dance-decoding or pheromone-coupling
   models could in principle inform colony-disruption strategies.
   The current dance decoder is a reduced-kernel baseline (nominal
   distance identity, not a calibrated decoder); only the
   follower-orientation diagnostics are anchored to published track
   data. The kernel is not optimized for disruption and the research
   suite does not score disruption metrics.

Each of these is a *future* concern, not a current capability, and
each is named here to make the boundary explicit.

## Provenance trail

The provenance trail is the foundation of every other claim in this
manuscript. The hydration pipeline links each manuscript variable to
its source artifact, each artifact to its generating script, each
script to a `src/beestack/` import, and each registered empirical
source to a DOI and license. A reader who suspects that a number has
drifted from its evidence can:

1. Open `output/data/manuscript_variables.json` to find the
   manuscript variable.
2. Follow the variable to its generating analysis artifact
   (`output/data/*.json` or `output/reports/*.json`).
3. Follow the artifact to its generating script in `scripts/`.
4. Follow the script to its imports in `src/beestack/`.
5. For empirical data, follow the registered source ID back to its
   DOI in this section.

This is the operational meaning of "honest research software":
every step is auditable and every gap is named.

## Closing note

Honey bees matter ecologically, economically, and scientifically
[@menzel2012honey; @seeley2010honeybee]. Because colony models can
influence ecological, agricultural, or robotic decisions, BeeStack
reports fidelity gaps, provenance, and current non-capabilities
alongside every generated result. Its evidence should be visible in
prose sections, figures, and JSON reports.
