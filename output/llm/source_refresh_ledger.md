# BeeStack Source Refresh Ledger

Perplexity/web discovery is recorded here only as a discovery channel. Manuscript evidence uses directly verified scholarly or official sources.

| Citation | DOI | Claim tier | Availability | Sections | Figures |
| --- | --- | --- | --- | --- | --- |
| `@vaxenburg2025flybody` | `10.1038/s41586-025-09029-4` | method_anchor | scholarly_open_metadata | `manuscript/05_methods_body_swarm.md`, `manuscript/08_validation_and_figures.md` | `output/figures/beebody_beeswarm_micro_macro_calibration.png` |
| `@becher2014beehave` | `10.1111/1365-2664.12222` | method_anchor | scholarly_open_metadata | `manuscript/05_methods_body_swarm.md`, `manuscript/07_methods_niche.md`, `manuscript/11_research_synthesis.md` | `output/figures/beebody_beeswarm_micro_macro_calibration.png`, `output/figures/beeniche_adapter_niche_map.png` |
| `@fair4rs2022principles` | `10.1038/s41597-022-01710-x` | validation_anchor | open_access_cc_by | `manuscript/03_materials_and_source_provenance.md`, `manuscript/15_reproducibility.md`, `manuscript/16_ethics_governance.md` | `output/figures/beestack_scholarship_evidence_matrix.png` |
| `@riley2005flightpaths` | `10.1038/nature03526` | method_anchor | scholarly_metadata | `manuscript/01_scholarship_and_related_work.md`, `manuscript/05_methods_body_swarm.md` | `output/figures/beebody_beeswarm_micro_macro_calibration.png` |
| `@landgraf2011roboticdance` | `10.1371/journal.pone.0021354` | method_anchor | open_access_cc_by | `manuscript/05_methods_body_swarm.md`, `manuscript/16_ethics_governance.md` | `output/figures/beebody_beeswarm_micro_macro_calibration.png` |
| `@hateren2019neuroethology` | `10.3390/insects10100336` | scholarship_anchor | open_access | `manuscript/01_scholarship_and_related_work.md`, `manuscript/06_methods_brain_mind.md` | `output/figures/beebrain_beemind_anatomy_policy_map.png` |
| `@oreskes1994verification` | `10.1126/science.263.5147.641` | validation_anchor | scholarly_metadata | `manuscript/08_validation_and_figures.md`, `manuscript/13_limitations.md` | `output/figures/beestack_validation_readiness_residuals.png` |
| `@bjornsson2020digitaltwins` | `10.1186/s13073-019-0701-3` | scholarship_anchor | open_access | `manuscript/14_roadmap.md`, `manuscript/16_ethics_governance.md` | `output/figures/beestack_validation_readiness_residuals.png` |
| `@dong2023wagglesocial` | `10.1126/science.ade1702` | scholarship_anchor | scholarly_metadata | `manuscript/01_scholarship_and_related_work.md`, `manuscript/05_methods_body_swarm.md` | `output/figures/beebody_beeswarm_micro_macro_calibration.png` |
| `@pnas2026waggleaudience` | `10.1073/pnas.2518687123` | scholarship_anchor | scholarly_metadata | `manuscript/01_scholarship_and_related_work.md`, `manuscript/05_methods_body_swarm.md` | `output/figures/beebody_beeswarm_micro_macro_calibration.png` |
| `@wallberg2019hav31` | `10.1186/s12864-019-5639-3` | scholarship_anchor | open_repository_not_wired | `manuscript/01_scholarship_and_related_work.md`, `manuscript/03_materials_and_source_provenance.md` | `output/figures/beestack_scholarship_evidence_matrix.png` |
| `@walsh2022hgd` | `10.1093/nar/gkab1018` | scholarship_anchor | open_repository_not_wired | `manuscript/01_scholarship_and_related_work.md`, `manuscript/03_materials_and_source_provenance.md` | `output/figures/beestack_scholarship_evidence_matrix.png` |
| `@rechlaval2025beebiome` | `10.1186/s12859-025-06229-7` | scholarship_anchor | open_repository_not_wired | `manuscript/01_scholarship_and_related_work.md`, `manuscript/03_materials_and_source_provenance.md`, `manuscript/14_roadmap.md` | `output/figures/beestack_scholarship_evidence_matrix.png` |
| `@dorey2023beebdc` | `10.1038/s41597-023-02626-w` | scholarship_anchor | open_repository_not_wired | `manuscript/01_scholarship_and_related_work.md`, `manuscript/03_materials_and_source_provenance.md`, `manuscript/07_methods_niche.md` | `output/figures/beestack_scholarship_evidence_matrix.png` |
| `@vanengelsdorp2009ccd` | `10.1371/journal.pone.0006481` | scholarship_anchor | scholarly_open_metadata | `manuscript/01_scholarship_and_related_work.md`, `manuscript/12_discussion.md` | `output/figures/beestack_scholarship_evidence_matrix.png` |
| `@scientificreports2026amitraz` | `10.1038/s41598-026-44796-8` | scholarship_anchor | scholarly_open_metadata | `manuscript/01_scholarship_and_related_work.md`, `manuscript/13_limitations.md`, `manuscript/14_roadmap.md` | `output/figures/beestack_scholarship_evidence_matrix.png` |

## External dataset registry (not yet wired)

| Resource | Type | DOI or URL | Target module | Wired | Blocker |
| --- | --- | --- | --- | --- | --- |
| `beebiome_portal` | microbiome_sra_index | `10.1186/s12859-025-06229-7` | BeeNiche/colony_ledger | no | Not registered in empirical_brain_datasets or BeeNiche driver parsers. |
| `hymenoptera_genome_database` | genomics_annotation | `10.1093/nar/gkab1018` | BeeBrain | no | Genome annotation not registered alongside HSB empirical anatomy IDs. |
| `beebdc_occurrence` | occurrence_aggregation | `10.1038/s41597-023-02626-w` | BeeNiche | no | Forage/landscape adapters use synthetic witnesses only. |
| `ncbi_amel_hav31` | reference_genome | `10.1186/s12864-019-5639-3` | BeeBrain | no | No genome-fetch stage in empirical pipeline. |
| `auburn_aia_survey` | colony_loss_survey | `https://apiaryinspectors.org/US-beekeeping-survey-24-25` | colony_ledger/assimilation | no | Survey microdata not ingested; scholarly continuity via @aurell2024survey only. |
| `usda_nass_honey` | agricultural_statistics | `https://esmis.nal.usda.gov/publication/honey` | colony_ledger | no | No NASS parser or assimilation surface in v0. |
| `epa_hive_matrices` | pesticide_residue_dataset | `10.23719/1523343` | BeeNiche | no | Pesticide burden not a typed BeeNiche state variable in v0. |
| `coloss_beebook` | methods_manual | `https://coloss.org/activities/beebook/` | methods/validation | no | Methods panels not yet mapped chapter-by-chapter to BEEBOOK volumes. |

## Notes

- `@vaxenburg2025flybody`: Anchors FlyBody/MuJoCo body and small-scene fidelity language.
- `@becher2014beehave`: Anchors BEEHAVE-compatible colony-summary and adapter claims.
- `@fair4rs2022principles`: Anchors FAIR software provenance, metadata, licensing, and reuse claims.
- `@riley2005flightpaths`: Anchors waggle-recruited flight-path and recruitment-boundary wording.
- `@landgraf2011roboticdance`: Anchors biomimetic dance-motion and robot-mediated hive-interaction context.
- `@hateren2019neuroethology`: Anchors follower-interaction and spatial-information language.
- `@oreskes1994verification`: Anchors separation of verification, validation, and confirmation.
- `@bjornsson2020digitaltwins`: Anchors conservative digital-twin readiness and governance framing.
- `@dong2023wagglesocial`: Anchors social-learning context for waggle recruitment interfaces.
- `@pnas2026waggleaudience`: Anchors bidirectional dance-audience communication context.
- `@wallberg2019hav31`: Anchors HAv3.1 reference genome context; not registered in BeeBrain fetch yet.
- `@walsh2022hgd`: Anchors HymenopteraMine/HGD genomics infrastructure context.
- `@rechlaval2025beebiome`: Anchors bee microbiome repository landscape; not wired into BeeNiche yet.
- `@dorey2023beebdc`: Anchors global bee occurrence aggregation; not wired into BeeNiche forage yet.
- `@vanengelsdorp2009ccd`: Anchors CCD historical context for colony-health motivation.
- `@scientificreports2026amitraz`: Anchors amitraz-resistance field context; Varroa not modeled in v0.

## Perplexity Discovery Candidates Not Promoted

| Candidate | DOI or URL | Status | Availability | Targets |
| --- | --- | --- | --- | --- |
| `biodt_honeybee_prototype` | https://riojournal.com/article/125167/ | discovery_only_not_promoted | official_article_page; code_data_payload_not_assessed | manuscript/14_roadmap.md; manuscript/16_ethics_governance.md / output/figures/beestack_validation_readiness_residuals.png |
| `hiveopolis_project_documentation` | https://cordis.europa.eu/project/id/824069 | discovery_only_not_promoted | official_project_page; empirical_payload_not_assessed | manuscript/07_methods_niche.md; manuscript/16_ethics_governance.md / output/figures/beeniche_adapter_niche_map.png |
| `vvug_digital_twin_survey` | https://pubmed.ncbi.nlm.nih.gov/39825103/ | discovery_only_not_promoted | PubMed record surfaced; DOI/license not promoted | manuscript/08_validation_and_figures.md; manuscript/13_limitations.md / output/figures/beestack_validation_readiness_residuals.png |

These candidates remain discovery records, not manuscript evidence.
