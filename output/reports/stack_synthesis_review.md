# BeeStack Cross-Stack Synthesis Review

Statistical synthesis of module readiness, simulation telemetry, visualization evidence, documentation signposting, empirical coverage, and manuscript scholarship.

## Global Statistics

- `empirical_parseable_fraction`: 0.600
- `known_gap_count_total`: 11.000
- `metric_count_total`: 60.000
- `module_artifact_coverage_fraction`: 1.000
- `module_readiness_mean`: 0.932
- `module_validation_mean`: 1.000
- `module_validation_min`: 1.000
- `module_validation_std`: 0.000
- `real_flybody_animation_count`: 5.000
- `reduced_schematic_animation_count`: 4.000
- `scholarship_reference_count`: 42.000
- `signposting_fraction`: 1.000
- `simulation_energy_drop_j`: 0.001
- `simulation_mean_wing_power_mw`: 58.291
- `simulation_policy_switch_count`: 0.000
- `simulation_recruited_total`: 168.000
- `simulation_step_count`: 24.000
- `simulation_thermal_error_improvement_c`: 4.415
- `visualization_artifact_count`: 66.000

## Module Panels

| Module | Fidelity | Validation | Readiness | Metrics | Evidence | Artifacts | Gaps |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BeeBody | FlyBody render path plus reduced closed-loop telemetry | 1.000 | 0.933 | 14 | 2 | 15 | 2 |
| BeeBrain | empirical reduced AL-MB-CX kernel | 1.000 | 0.933 | 14 | 3 | 25 | 2 |
| BeeMind | bounded active-inference-style policy kernel | 1.000 | 0.933 | 9 | 2 | 9 | 2 |
| BeeSwarm | reduced communication kernel plus strict FlyBody/MuJoCo BeeBody waggle/collision scenes | 1.000 | 0.925 | 14 | 2 | 18 | 3 |
| BeeNiche | voxel comb and thermal kernel with adapter schemas | 1.000 | 0.933 | 9 | 2 | 11 | 2 |

## Validations

- `module_coverage`: pass; value `5`; threshold `5`. Body, Brain, Mind, Swarm, and Niche all appear in synthesis.
- `validation_target`: pass; value `1.0`; threshold `0.9`. Mean module validation fraction meets synthesis target.
- `artifact_coverage`: pass; value `1.0`; threshold `1.0`. Each module has visualization or evidence artifacts.
- `documentation_signposting`: pass; value `1.0`; threshold `1.0`. Every non-cache directory has README.md and AGENTS.md coverage.
- `empirical_parseability`: pass; value `0.6`; threshold `0.5`. BeeBrain parseable-source fraction clears configured minimum.
- `simulation_energy_finite`: pass; value `0.000821`; threshold `>= 0`. Body energy does not increase during the deterministic integrated run.
- `simulation_thermal_improves`: pass; value `4.415`; threshold `> 0`. Brood-temperature error improves over the deterministic run.
- `scholarship_minimum`: pass; value `42`; threshold `7`. Manuscript bibliography includes the configured minimum scholarship anchors.

## Prioritized Findings

- Weakest synthesized module is BeeSwarm (readiness 0.925; gaps 3).
- Cross-stack validation mean is 1.000 with 11 catalogued module gaps.
- Integrated simulation improved brood-temperature error by 4.415 C over 24 steps.
- All synthesis validation gates passed in the latest generated run.

## Scholarship Anchors

- `@andreu2025dryad`
- `@becher2014beehave`
- `@bjornsson2020digitaltwins`
- `@carcaud2022dryad`
- `@couvillon2014waggle`
- `@free1987pheromones`
- `@friedman2026beestack`
- `@friston2010free`
- `@galizia1999glomerular`
- `@hadjitofi2024figshare`
- `@honkanen2019sky`
- `@jernigan2026dryad`
- `@johnson2009self`
- `@johnson2010temporal`
- `@kaneko2016kenyon`
- `@khamassi2020bio`
- `@kronenberg1982colonial`
- `@menzel2001cognitive`
- `@menzel2012honey`
- `@millman2020scientific`
- `@mitchell2019modelcards`
- `@nagari2017waggle`
- `@narsicht2020hiveopolis`
- `@nouvian2017dryad`
- `@oreskes1994verification`
- `@paoli2024dryad`
- `@parr2017working`
- `@pfeifer2006morphological`
- `@rybak2010digital`
- `@saltelli2008global`
- `@sasaki2018superorganisms`
- `@seeley1989superorganism`
- `@seeley2003consensus`
- `@seeley2010honeybee`
- `@stone2017central`
- `@szyszka2023granger`
- `@todorov2012mujoco`
- `@vaxenburg2025flybody`
- `@wcislo2003respiratory`
- `@webb2020waggle`
- `@wilkinson2016fair`
- `@wilson2017good`

## Figures

- `/Users/4d/Documents/GitHub/template/projects_in_progress/BeeStack/output/figures/research/stack_synthesis_dashboard.png`
