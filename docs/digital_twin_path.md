# Digital-Twin Path

BeeStack can become a full systems-biology colony and population-of-colonies digital twin only if the current scaffold gains four things that are not yet present everywhere:

1. **State breadth** across omics, physiology, behavior, colony demography, nest/landscape drivers, and regional colony networks.
2. **Assimilation** from longitudinal observations, not just deterministic replay of configured scenarios.
3. **Validation residuals** against held-out biological data at every scale.
4. **Governance boundaries** that mark forecasts, counterfactuals, and decision-support outputs as research claims until validated for a concrete operational use.

The current project should therefore describe itself as an evidence-typed scaffold with a digital-twin target, not as if that target had already been reached.

## Machine-readable assessment

Run:

```bash
uv run python scripts/assess_digital_twin_readiness.py
```

Generated artifacts:

- `output/data/digital_twin_readiness.json` — requirement catalog, maturity scores, scale summaries, top blockers, and next artifacts.
- `output/reports/digital_twin_readiness.md` — human-readable review.

The assessment currently names these required scales:

| Scale | Required expansion |
| --- | --- |
| Molecular / omics | transcriptomics, metabolomics, microbiome, immune, pathogen, pesticide, and nutritional state |
| Cell / tissue physiology | endocrine, immune, reproductive, brood, mortality, and nutrition dynamics |
| Individual bee | calibrated FlyBody physics, sensory noise, neural dynamics, learning tasks, and energy residuals |
| Colony system | queen laying, brood cohorts, resource stores, disease, task allocation, and BEEHAVE-comparable demography |
| Nest / landscape | weather, land cover, floral phenology, pesticide exposure, hive-management events, and nest sensor assimilation |
| Population of colonies | apiary/feral colony networks, pathogen transmission, queen/drone mating, migration, robbing, drifting, genetics, and regional loss validation |
| Assimilation / control | posterior uncertainty, forecast skill, intervention counterfactuals, and held-out seasonal outcomes |
| Governance / provenance | model cards, license checks, evidence tiers, uncertainty language, and decision-support boundaries |

## Architecture upgrade

A full twin should be built as a set of explicit strata rather than a single larger simulator:

1. **Measurement layer** — parsers for hive scales, counters, weather, imaging, omics, pathogen assays, pesticide assays, management logs, apiary inspections, and remote sensing.
2. **State layer** — typed colony, bee, brood, resource, pathogen, molecular, landscape, and population-network states with units and provenance.
3. **Process layer** — mechanistic or hybrid models for physiology, biomechanics, neural learning, recruitment, demography, thermal regulation, foraging, disease, and genetics.
4. **Assimilation layer** — state-space or Bayesian updating that fits parameters and latent states from observations.
5. **Validation layer** — held-out residuals, posterior predictive checks, and scenario comparisons for each scale.
6. **Forecast/control layer** — counterfactual management and environmental scenarios with uncertainty intervals and explicit use boundaries.

## Near-term build order

The highest-leverage path is not to jump directly to a giant population simulator. Build the twin in this order:

1. **Colony state ledger**: brood, adult castes, queen laying, stores, mortality, pathogen loads, and interventions. This becomes the conservation backbone.
2. **Driver ingestion**: weather, floral resources, hive sensors, apiary inspections, pathogen/pesticide assays, and management events indexed by colony and date.
3. **BEEHAVE parity**: reproduce documented BEEHAVE scenarios under identical assumptions before adding richer BeeStack-specific mechanisms.
4. **Assimilation prototype**: fit a small seasonal colony model to held-out hive observations with posterior predictive checks.
5. **Population network**: add apiaries/feral colonies, drifting/robbing, queen/drone mating, pathogen transmission, and landscape competition.
6. **Systems-biology layer**: map omics/pathogen/pesticide/nutritional measurements onto physiology parameters and uncertainty.
7. **Operational governance**: keep forecasts marked as research until the validation target, use case, data rights, and failure modes are explicit.

## Acceptance criteria for calling it a digital twin

BeeStack should not claim to be a full colony/population digital twin until all of the following are true:

- every scale has a typed state schema with units, provenance, and update rules;
- all core flows conserve individuals, resource mass, or explicitly documented quantities;
- longitudinal observations are assimilated, not merely plotted after simulation;
- held-out forecast skill is reported against external observations;
- calibration residuals are reported for Body, Brain, Mind, Swarm, Niche, colony, and population layers;
- population-of-colonies scenarios include disease, drift/robbing, migration, mating/genetics, and regional validation;
- counterfactual interventions include uncertainty intervals and assumptions;
- governance artifacts make the difference between research forecast, hypothesis generator, and validated decision-support tool explicit.
