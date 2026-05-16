# Abstract

BeeStack is an executable research scaffold for a whole-of-colony digital twin
of the Western honey bee, *Apis mellifera*. It converts a five-layer
biophysical specification — body, brain, mind, swarm, and niche — into
{{MODULE_COUNT}} typed Python modules with explicit contracts, deterministic
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

The stack is seeded with `{{CONFIG_SEED}}`, runs a {{CONTROL_RATE_HZ}} Hz
observation–action boundary on top of a {{PHYSICS_DT_MS}} ms physics step,
and hydrates this manuscript from variables generated at run time. The
default configuration preserves {{GLOMERULI}} antennal-lobe glomeruli,
{{KC_PER_HEMISPHERE}} Kenyon cells per hemisphere with sparse mushroom-body
activity at $\rho = {{KC_SPARSITY}}$ (yielding {{ACTIVE_KC}} active Kenyon
cells), {{HEADING_BINS}} central-complex heading bins
[@stone2017central; @honkanen2019sky], and a {{WING_STROKE_HZ}} Hz wing
stroke. The empirical run currently integrates {{EMPIRICAL_PANEL_COUNT}}
response panels, {{ANATOMY_INVENTORY_COUNT}} anatomy inventories,
{{ANTENNAL_SUMMARY_COUNT}} antennal-movement summaries, and
{{EMPIRICAL_TEMPLATE_COUNT}} odor templates, with a parseable-source
fraction of {{BRAIN_DATA_PARSEABLE_FRACTION}}. The research suite reports
{{RESEARCH_VISUALIZATION_COUNT}} visualization artifacts,
{{RESEARCH_SWEEP_COUNT}} deterministic sensitivity sweeps,
{{RESEARCH_EVIDENCE_COUNT}} empirical evidence records, and an overall
validation fraction of {{RESEARCH_VALIDATION_FRACTION}}. The methods-analysis
pass adds {{METHODS_PANEL_COUNT}} module dashboards,
{{METHODS_FIGURE_COUNT}} static methods figures, and
{{METHODS_EVIDENCE_LINK_COUNT}} manuscript-evidence cross-links.

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
