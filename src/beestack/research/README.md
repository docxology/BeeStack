# BeeStack Research Suite

Typed research-report assembly for module method scorecards, visualization
inventories, empirical evidence summaries, deterministic sensitivity sweeps,
and science-first methods-analysis panels. Keep file I/O in scripts; this
package should assemble records from payloads and run pure computations.

`suite.py` owns the central `ResearchSuiteReport`.
`methods.py` owns `MethodsAnalysisReport`, module methods panels, validation
panels, visualization panels, scenario sweep panels, and manuscript evidence
links.
`synthesis.py` owns `StackSynthesisReview`, a cross-stack statistical layer over
module readiness, simulation telemetry, visualization artifacts, empirical
parseability, signposting, and manuscript scholarship anchors.

Research records separate four surfaces: implementation verification, empirical
validation, sensitivity, and applicability. Raising a module's evidence tier or
digital-twin readiness requires matching generated artifacts and validation
residuals, not just stronger prose.

Empirical and manuscript evidence availability is typed. Use only
`parsed`, `generated`, `registered_absent`, `network_gated_absent`, or
`missing_optional`; absent BeeBrain payloads must remain explicit availability
states rather than manuscript support claims.

Figure inventories use one sorted project-relative path per artifact. Orchestrators
pass `project_root` and an `artifact_metadata` mapping of paths to authoritative
sidecar payloads into research/methods assembly; pure assemblers never load those
files themselves. Backend, fidelity, source data, validation status, and generating
command survive methods panels and the manuscript index without generic overrides.
Missing sidecars remain `unrecorded`/`metadata_unavailable`, not inferred validation.
The optional visualization `availability_status` is also retained end-to-end;
the I/O owner may mark retained historical empirical figures `historical_unavailable`
without erasing their original source/render provenance or claiming current evidence.
