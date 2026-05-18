# Perplexity Documentation And Validation Audit

- Date: 2026-05-18
- Command: `llm -m sonar-deep-research 'As of May 2026, review best practices for documenting and validating an open-source Python research software project like BeeStack...'`
- Purpose: External source-refresh for BeeStack README/AGENTS, testing, generated-output, empirical-data, and digital-twin boundary documentation.

## Applied Findings

- FAIR-style provenance remains the right framing for `output/data/empirical_sources/`, generated JSON, report sidecars, and manuscript variables: metadata, license/source, processing path, and provenance must stay explicit.
- JOSS-style research-software review expectations support BeeStack's `uv` setup, automated tests, examples, CI, and objective functionality checks.
- Biological-model validation should stay separate from software verification. BeeStack tests can prove implementation contracts, but biological calibration claims need named external data, residuals, sensitivity checks, and applicability limits.
- Digital-twin language must remain conservative until there is longitudinal assimilation, held-out forecast skill, uncertainty/residual reporting, and governance around decision-support use.
- Generated artifacts should carry enough lineage for reviewers to move from source module to script, output, validation surface, and manuscript claim without inference.
- Optional empirical analysis should be documented as network/data gated: absent payloads are an availability state, not a reason to fabricate replacement values.

## Sources To Recheck On Future Refreshes

- FAIR Principles: https://www.go-fair.org/fair-principles/
- JOSS review criteria: https://joss.readthedocs.io/en/latest/review_criteria.html
- Digital Twin Consortium Business Maturity Model: https://www.digitaltwinconsortium.org/publications/digital-twin-business-maturity-model/
- Unit Testing, Model Validation, and Biological Simulation: https://pmc.ncbi.nlm.nih.gov/articles/PMC5007758/
- Documenting research in simulation science: https://pmc.ncbi.nlm.nih.gov/articles/PMC11541550/
- Reproducibility of computational workflows is automated using continuous analysis: https://pmc.ncbi.nlm.nih.gov/articles/PMC6103790/
- Honey Bee Dance Language overview: https://content.ces.ncsu.edu/honey-bee-dance-language
- FlyBody upstream repository: https://github.com/TuragaLab/flybody
- Hadjitofi-Webb waggle-following dataset: https://figshare.com/articles/dataset/Honeybee_antennal_positioning_data_when_following_dances/24715977

## Documentation Paths Updated From This Refresh

- `README.md`
- `docs/generated_outputs.md`
- `docs/research_operations_playbook.md`
- `docs/testing_philosophy.md`
- `docs/validation_criteria.md`
- `docs/beebrain_data_pipeline.md`
- `docs/empirical_beebrain.md`
- `docs/troubleshooting.md`
- `docs/signposting.md`
- `output/llm/README.md`
- `output/logs/README.md`
- `output/simulations/README.md`
- `output/tex/README.md`
- `output/pdf/README.md`
- `output/slides/README.md`
- `output/web/README.md`
