# BeeStack Cross-Stack Synthesis Review

Statistical synthesis of module readiness, simulation telemetry, visualization evidence, documentation signposting, empirical coverage, and manuscript scholarship.

## Global Statistics

- `empirical_parseable_fraction`: 0.000
- `known_gap_count_total`: 11.000
- `metric_count_total`: 61.000
- `module_artifact_coverage_fraction`: 1.000
- `module_readiness_mean`: 0.842
- `module_validation_mean`: 0.800
- `module_validation_min`: 0.000
- `module_validation_std`: 0.400
- `real_flybody_animation_count`: 5.000
- `reduced_schematic_animation_count`: 4.000
- `scholarship_reference_count`: 93.000
- `signposting_fraction`: 1.000
- `simulation_energy_drop_j`: 0.001
- `simulation_mean_wing_power_mw`: 58.291
- `simulation_policy_switch_count`: 0.000
- `simulation_recruited_total`: 168.000
- `simulation_step_count`: 24.000
- `simulation_thermal_error_improvement_c`: 3.964
- `visualization_artifact_count`: 75.000

## Module Panels

| Module | Fidelity | Validation | Readiness | Metrics | Evidence | Artifacts | Gaps |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BeeBody | FlyBody render path plus reduced closed-loop telemetry | 1.000 | 0.933 | 14 | 2 | 22 | 2 |
| BeeBrain | empirical reduced AL-MB-CX kernel | 0.000 | 0.483 | 15 | 3 | 29 | 2 |
| BeeMind | bounded active-inference-style policy kernel | 1.000 | 0.933 | 9 | 2 | 9 | 2 |
| BeeSwarm | reduced communication kernel plus strict FlyBody/MuJoCo BeeBody waggle/collision scenes | 1.000 | 0.925 | 14 | 2 | 23 | 3 |
| BeeNiche | voxel comb and thermal kernel with adapter schemas | 1.000 | 0.933 | 9 | 2 | 12 | 2 |

## Validations

- `module_coverage`: pass; value `5`; threshold `5`. Body, Brain, Mind, Swarm, and Niche all appear in synthesis.
- `validation_target`: gap; value `0.8`; threshold `0.9`. Mean module validation fraction does not meet synthesis target.
- `artifact_coverage`: pass; value `1.0`; threshold `1.0`. Each module has visualization or evidence artifacts.
- `documentation_signposting`: pass; value `1.0`; threshold `1.0`. Every non-cache directory has README.md and AGENTS.md coverage.
- `empirical_parseability`: gap; value `0.0`; threshold `0.5`. BeeBrain parseable-source fraction does not clear configured minimum.
- `simulation_energy_finite`: pass; value `0.000821`; threshold `>= 0`. Body energy does not increase during the deterministic integrated run.
- `simulation_thermal_improves`: pass; value `3.964`; threshold `> 0`. Brood-temperature error improves over the deterministic run.
- `scholarship_minimum`: pass; value `93`; threshold `7`. Manuscript bibliography includes the configured minimum scholarship anchors.

## Prioritized Findings

- Weakest synthesized module is BeeBrain (readiness 0.483; gaps 2).
- Cross-stack validation mean is 0.800 with 11 catalogued module gaps.
- Integrated simulation improved brood-temperature error by 3.964 C over 24 steps.
- Open synthesis validation gates: validation_target, empirical_parseability.

## Scholarship Anchors

- `@ahsan2025neonic`
- `@andreu2025alarmor`
- `@andreu2025dryad`
- `@auburn2025survey`
- `@aurell2024survey`
- `@becher2014beehave`
- `@bjornsson2020digitaltwins`
- `@brandt2005standardbrain`
- `@brown2021royaljelly`
- `@bruckner2023survey`
- `@carcaud2022dryad`
- `@chege2025forage`
- `@chen2016genomic`
- `@cleveland1984graphical`
- `@colossbeebook`
- `@couvillon2014waggle`
- `@crameri2020colour`
- `@cridland2017demography`
- `@dong2023wagglesocial`
- `@dorey2023beebdc`
- `@epa2024hivematrices`
- `@evans2006immune`
- `@fair4rs2022principles`
- `@free1987pheromones`
- `@friedman2026beestack`
- `@friston2010free`
- `@g3journal2023scrna`
- `@galizia1999glomerular`
- `@geneticdiversity2022microbiome`
- `@glinski2024hivematrices`
- `@hadjitofi2024currentbiology`
- `@hadjitofi2024figshare`
- `@hateren2019neuroethology`
- `@heer2012interactive`
- `@highfield2009dwv`
- `@hisamoto2024landscape`
- `@hiveopolis2019project`
- `@honeybee2006genome`
- `@honkanen2019sky`
- `@jernigan2026dryad`
- `@johnson2010temporal`
- `@kaneko2016kenyon`
- `@khamassi2020bio`
- `@kronenberg1982colonial`
- `@kwong2016gutmicrobiome`
- `@lactobacilli2025winter`
- `@lamprecht2020fairsoftware`
- `@landgraf2011roboticdance`
- `@landuse2024nutrition`
- `@menzel2001cognitive`
- `@menzel2005map`
- `@menzel2012honey`
- `@microbiome2024winter`
- `@millman2020scientific`
- `@mitchell2019modelcards`
- `@mondet2018hygienic`
- `@nagari2017waggle`
- `@naturecomm2025metagenomics`
- `@naturecomm2025spatialbrain`
- `@nouvian2017dryad`
- `@oreskes1994verification`
- `@paoli2024dryad`
- `@parr2017working`
- `@pfeifer2006morphological`
- `@pnas2026waggleaudience`
- `@pollination2016value`
- `@ragan2016provenance`
- `@rechlaval2025beebiome`
- `@riley2005flightpaths`
- `@rougier2014figures`
- `@rybak2010digital`
- `@saltelli2008global`
- `@sasaki2018superorganisms`
- `@scientificreports2026amitraz`
- `@scitotenv2024varroameta`
- `@scitotenv2025triage`
- `@seeley1989superorganism`
- `@seeley2003consensus`
- `@seeley2010honeybee`
- `@stone2017central`
- `@szyszka2023granger`
- `@todorov2012mujoco`
- `@vanengelsdorp2009ccd`
- `@vaxenburg2025flybody`
- `@w3c2023wcag21`
- `@wallberg2019hav31`
- `@walsh2022hgd`
- `@wario2015automatic`
- `@webb2020waggle`
- `@wilfert2022dwv`
- `@wilkinson2016fair`
- `@wilson2017good`
- `@zheng2018mbio`

## Figures

- `output/figures/research/stack_synthesis_dashboard.png`
- `output/figures/research/stack_synthesis_findings_detail.png`
