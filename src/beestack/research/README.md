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

Empirical and manuscript evidence availability is typed: `parsed`, `generated`,
`registered_absent`, `network_gated_absent`, `missing_optional`, and
`analysis_unavailable`. A missing current aggregate uses `analysis_unavailable`:
its zero represented records are not an observation that standalone files are
absent. Report parseability and evidence credit describe supplied current analysis,
not the raw acquisition inventory. Waggle presence uses the explicit dataset
availability flag, never a positive confidence score. Unavailable current evidence
cannot support manuscript claims.

Finite diagnostic maps omit unobserved empirical means rather than manufacturing
measurements. Observed zero means remain present; zero counts or conservative
evidence-credit scores do not establish an observed mean.

Figure inventories use one sorted project-relative path per artifact. Orchestrators
pass `project_root` and an `artifact_metadata` mapping of paths to authoritative
sidecar payloads into research/methods assembly; pure assemblers never load those
files themselves. Backend, fidelity, source data, validation status, and generating
command survive methods panels and the manuscript index without generic overrides.
Missing sidecars remain `unrecorded`/`metadata_unavailable`, not inferred validation.
The optional visualization `availability_status` is also retained end-to-end;
the I/O owner may mark retained historical empirical figures `historical_unavailable`
without erasing their original source/render provenance or claiming current evidence.

Scenario sweep panels retain the original nullable `outputs` at every parameter
coordinate. `observation_counts` are derived from those observations, not supplied
independently. Output lengths must match the finite parameter coordinates, and every
observed output must be a finite number. `output_ranges` are null for any absent or
partial series; `unavailable_outputs` identifies those series. Only complete series
can be `varying_outputs` (positive range), `insensitive_outputs` (zero range), or
varying `monotonic_outputs`. A measured all-zero series is therefore insensitive;
an all-null or partly observed series is not. Native-unit ranges are reported per
output, never ranked across different units as a dominant signal.

Methods analysis requires nonempty research sensitivity sweeps: there is no
optional-research configuration switch, and `MethodsAnalysisReport` already
requires scenario panels. Missing sweeps raise a clear `ValueError` before module
assembly instead of fabricating a `not_yet_generated` zero panel. Missing empirical
alignment within an otherwise valid sweep remains available as explicit null
observations, not a reason to fabricate a range or weaken validation gates.

## Observation support and configured self-test denominators

Research validation values, module metric maps and synthesis statistics may be
null when observations are absent, unparseable, boolean or nonfinite. Actual zero
remains numeric zero. An unavailable numeric witness fails its check and remains
in the validation denominator; configured-parameter and declared-gap checks keep
their separate meanings. Synthesis energy/thermal changes require complete finite
record support, including intermediate rows; independent valid channels survive
partial records. Signed degradation is not clipped into improvement.

Methods telemetry images/raw data share these gaps without an empty-run sample.
Tables and manuscript metrics show unavailable values explicitly. Metric-field
inventory counts include declared fields, not biological samples or necessarily
observed quantities. Configured self-test fractions remain software diagnostics,
not empirical validation or colony realism.
