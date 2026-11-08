# Abstract {#sec:abstract}

BeeStack is an executable research scaffold for whole-colony simulation
of the Western honey bee, *Apis mellifera*. It converts a five-layer
biophysical specification — body, brain, mind, swarm, and niche — into
5 typed Python modules with explicit contracts, deterministic
seeding, and a continuous evidentiary trail running from raw configuration to
hydrated manuscript. The implementation is deliberately tiered. BeeBody uses
FlyBody [@vaxenburg2025flybody] walking and wing-beat flight tasks
through a generated honeybee MJCF body plan rendered in MuJoCo
[@todorov2012mujoco]; strict BeeSwarm waggle and collision scenes use
full BeeBody MJCF copies inside the same physics engine with required contact
metrics, while remaining scripted small-scene visual/contact witnesses rather
than integrated colony dynamics; BeeBrain ingests curated public
*Apis mellifera* anatomy and activity datasets — including the Honey-Bee
Standard Brain atlas and integration ecosystem
[@brandt2005standardbrain; @rybak2010digital], glomerular odor codes
[@galizia1999glomerular], calcium imaging
[@paoli2024dryad; @carcaud2022dryad; @szyszka2023granger], Kenyon-cell
subtype gene expression [@kaneko2016kenyon], alarm-pheromone receptors
[@andreu2025dryad], antennal active-sensing kinematics
[@jernigan2026dryad], biogenic-amine spreadsheets [@nouvian2017dryad],
and Hadjitofi–Webb dance-follower antennal positioning
[@hadjitofi2024figshare; @hadjitofi2024currentbiology] — and converts them into typed anatomy
inventories, response panels, and dance-decoding templates; while BeeMind,
the non-visual swarm communication kernel, and BeeNiche remain reduced
deterministic kernels with explicit contracts and labeled gaps.

Field-scale colony-health stressors—mites, viruses, pesticides, and
survey-documented losses—motivate the roadmap's colony ledger and assimilation
surfaces [@sec:roadmap], but the current BeeStack implementation does not model those drivers as
typed state.

The stack is seeded with `20260513` and hydrates this manuscript from
variables generated at run time. Its reduced loop advances at a configured
100 Hz control boundary; the 0.5 ms physics
setting is not executed as MuJoCo substeps inside that loop. The
default configuration preserves 170 antennal-lobe glomeruli,
170,000 Kenyon cells per hemisphere with sparse mushroom-body
activity at $\rho = 0.02$ (yielding 6,800 active Kenyon
cells across both hemispheres), 32 central-complex heading bins
[@stone2017central; @honkanen2019sky], and a 230 Hz wing
stroke. Empirical availability is `historical_unavailable`. When
local payloads support a fresh analysis, its inventory contains
N/A response panels, N/A
anatomy inventories, N/A antennal summaries, and
N/A odor templates; unavailable values remain N/A.
The parseable-source fraction is N/A. The research suite reports
75 visualization artifacts,
3 deterministic sensitivity sweeps, and
5 empirical evidence records. Registered module
contract checks yield a config-band self-test rate of
0.750, measured alongside
11 explicitly catalogued open gaps. This
rate measures configured contract checks, not biological validation. The methods-analysis
pass adds 5 module dashboards,
8 static methods figures, and
6 manuscript-evidence cross-links.

BeeStack does not claim to be a finished biological simulator. Its
contribution is a reproducible substrate that keeps FlyBody/MuJoCo
outputs, empirical BeeBrain evidence, reduced kernels, validation reports,
and acknowledged gaps separate enough to improve incrementally without
losing the whole-system contract. By treating fidelity as a declared
property of each module rather than an unmarked global ambition, BeeStack
makes it possible to replace one layer at a time — for example,
substituting a spiking BeeBrain dynamics core or a BEEHAVE-scale
[@becher2014beehave] colony backend — while preserving the cross-layer
data contracts that make multi-scale honeybee modeling reproducible
[@wilson2017good].
