# Integrated Results from the Reduced Scenario {#sec:integrated_results}

This section reports a seeded, reduced multi-module scenario, not a whole-colony
closed loop or proof that every declared cross-layer contract executes. A fixed
synthetic dance updates BeeMind beliefs and BeeSwarm recruitment diagnostics;
selected policies drive reduced BeeBody actions, and Body observations enter
BeeBrain. BeeNiche temperature advances independently. BrainState does not feed
policy selection, niche context does not feed the Body step, and recruitment
does not retask stored agents. The module inventory records available contracts,
not measured edge coverage or biological integration.

## Reduced-loop endpoint and recruitment diagnostics

The deterministic integrated run completed 24 control
steps at the configured 100 Hz boundary. The final
selected policy was `nurse_brood`, the final body speed was
0.004 m/s, the final body-frame energy budget was
23.999 J, and the mean wing power across the rollout was
58.291 mW. Summed per-tick recruitment matches total
168; an agent may be counted on multiple ticks. This is not a
unique-follower count or evidence of realized task reassignment.

The final comb occupancy fraction was 0.083, and the
brood-temperature error at the final step was
2.875 °C from the configured 34
°C target [@kronenberg1982colonial]. The optional template-bank diagnostic
reports odor `N/A` and alignment
N/A when compatible templates are supplied; without
that bank the diagnostic is unavailable, not a measured zero. It neither drives
the fixed synthetic dance scenario nor establishes biological validation.

## Energy, comb, and module-inventory witnesses

The three witnesses below summarize the integrated run recorded in
`output/data/run_summary.json` and `simulation_records.json`. Each figure is a
reduced-kernel diagnostic with an explicit sidecar boundary.

[@fig:body_energy] traces BeeBody energy witnesses across the integrated run.

![Integrated-run BeeBody energy witness showing deterministic reduced energy accounting across control steps. Generated from output/data/simulation_records.json using Matplotlib. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not calibrate honeybee energetics.](../figures/body_energy_timeseries.png){#fig:body_energy}

[@fig:comb_fraction] traces BeeNiche comb occupancy across the integrated run.

![Integrated-run comb-occupancy witness showing deterministic BeeNiche state changes across control steps. Generated from output/data/simulation_records.json using Matplotlib. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not validate full hive ecology.](../figures/comb_fraction_timeseries.png){#fig:comb_fraction}

[@fig:module_coverage] lists the supplied module contract inventory, not executed-edge coverage.

![Module names present in the supplied contract inventory. Presence is not an edge-coverage score, behavioral proof, or biological validation. Generated from output/data/module_coverage.json using Matplotlib. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not prove scientific validation completeness.](../figures/module_contract_coverage.png){#fig:module_coverage}

## Run-summary and per-step artifact provenance

The run summary is not a one-off console transcript. The values in this
section are written to `output/data/run_summary.json`, the per-step
records are written to `output/data/simulation_records.json`, and the
contract coverage witness is written to `output/data/module_coverage.json`.
The same pipeline writes `output/data/animation_manifest.json`,
`output/reports/beestack_integrity_review.md`, and the hydrated sections
under `output/manuscript/`. That trace makes the integrated run auditable:
if a figure or sentence changes, the corresponding JSON or report changes
with it.

## Reproducibility diagnostics without biological validation

These are reproducibility witnesses, not biological validation. The seeded
five-module driver produces inspectable intermediate records and figures from
one configuration. A repeatability claim must compare named outputs at matching
source, configuration, inputs, and runtime; a seed alone does not guarantee every
number across environments, byte-identical rendering, or unchanged timestamped
reports. Contract validity is checked separately from numerical agreement.

The empirical-alignment score should be read especially conservatively.
The current BeeBrain empirical layer projects available odor templates
into a reduced AL–MB–CX path; the alignment metric measures whether
the projected MB activity matches the expected template signature, not
whether the underlying neural model is biologically calibrated. A high
alignment score with the current kernel is a sanity check that the
template-bank pipeline is wired correctly; it is not a claim about
neural predictive validity. The full predictive validity claim lives
in the roadmap.

## Unsupported population, biomechanics, policy, and thermal claims

The integrated run does not claim:

1. **Population-scale dynamics** — recruitment numbers come from the
   reduced communication kernel, not from a BEEHAVE-scale
   demographic engine.
2. **Calibrated biomechanics** — the energy and wing-power numbers
   come from the reduced energetics model, not from a measured
   honey-bee biomechanics dataset.
3. **Learned policy quality** — `nurse_brood` is the
   highest-scoring policy under the hand-configured
   active-inference-style scorer; it is not the output of a learned
   colony-optimal controller or BrainState feedback.
4. **Real-time thermoregulation accuracy** — the brood-temperature
   error number measures whether the kernel keeps the target band
   approximately, not whether the dynamics match real hive thermal
   response curves [@kronenberg1982colonial].

The supported positive claim is an inspectable reduced scenario with typed
interfaces and provenance-bound artifacts. Selected interfaces execute while
other feedback routes remain declared. This is the present meaning of executable
architecture here, not evidence of a calibrated whole-colony system.

## Links to module methods and empirical results

Where the run touches a specific module, the relevant per-module
results section provides the depth: BeeBody for the energetics and rendering,
BeeBrain for the AL–MB–CX trace, BeeMind for the policy-score landscape,
BeeSwarm for the recruitment and contact pairs, and BeeNiche for the comb and
thermal traces. Empirical anchor data are summarized in [@sec:empirical_results];
the research-suite
scorecards and known-gaps catalog are in [@sec:research_synthesis].
