# Abstract

BeeStack is an executable research scaffold for a whole-of-colony digital twin
of the Western honey bee, *Apis mellifera*. It converts a five-layer
biophysical specification — body, brain, mind, swarm, and niche — into
5 typed Python modules with explicit contracts, deterministic
seeding, and a continuous evidentiary trail running from raw configuration to
hydrated manuscript. The implementation is deliberately tiered. BeeBody uses
real FlyBody [@vaxenburg2025flybody] walking and wing-beat flight tasks
through a generated honeybee MJCF body plan rendered in MuJoCo
[@todorov2012mujoco]; BeeSwarm production waggle and collision scenes step
full BeeBody MJCF copies inside the same physics engine with required contact
metrics; BeeBrain ingests curated public *Apis mellifera*
anatomy and activity datasets — including the Honey Bee Standard Brain
ecosystem [@rybak2010digital], glomerular odor codes [@galizia1999glomerular],
calcium imaging [@paoli2024dryad; @carcaud2022dryad; @szyszka2023granger],
Kenyon-cell subtype gene expression [@kaneko2016kenyon], alarm-pheromone
receptors [@andreu2025dryad], antennal active-sensing kinematics
[@jernigan2026dryad], biogenic-amine spreadsheets [@nouvian2017dryad], and
Hadjitofi–Webb dance-follower antennal positioning
[@hadjitofi2024figshare] — and converts them into typed anatomy
inventories, response panels, and dance-decoding templates; while BeeMind,
the non-visual swarm communication kernel, and BeeNiche remain reduced
deterministic kernels with explicit contracts and labeled gaps.

The stack is seeded with `20260513`, runs a 100 Hz
observation–action boundary on top of a 0.5 ms physics step,
and hydrates this manuscript from variables generated at run time. The
default configuration preserves 170 antennal-lobe glomeruli,
170,000 Kenyon cells per hemisphere with sparse mushroom-body
activity at $\rho = 0.02$ (yielding 6,800 active Kenyon
cells), 32 central-complex heading bins
[@stone2017central; @honkanen2019sky], and a 230 Hz wing
stroke. The empirical run currently integrates 48
response panels, 7 anatomy inventories,
1 antennal-movement summaries, and
24 odor templates, with a parseable-source
fraction of 0.600. The research suite reports
66 visualization artifacts,
3 deterministic sensitivity sweeps,
5 empirical evidence records, and an overall
validation fraction of 1.000. The methods-analysis
pass adds 5 module dashboards,
7 static methods figures, and
6 manuscript-evidence cross-links.

BeeStack does not claim to be a finished biological simulator. Its
contribution is a reproducible substrate that keeps real FlyBody/MuJoCo
outputs, empirical BeeBrain evidence, reduced kernels, validation reports,
and acknowledged gaps separate enough to improve incrementally without
losing the whole-system contract. By treating fidelity as a declared
property of each module rather than an unmarked global ambition, BeeStack
makes it possible to replace one layer at a time — for example,
substituting a spiking BeeBrain dynamics core or a BEEHAVE-scale
[@becher2014beehave] colony backend — while preserving the cross-layer
data contracts that make multi-scale honeybee modeling reproducible
[@wilson2017good].
