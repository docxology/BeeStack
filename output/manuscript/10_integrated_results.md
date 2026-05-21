# Integrated Results

This section reports the *deterministic integrated run* — the single
closed-loop rollout that exercises every cross-layer contract. It is
the smallest claim BeeStack makes that is genuinely *whole-of-colony*:
a bee observes through BeeBody, decides through BeeBrain and BeeMind,
acts back on BeeBody, and the result propagates through BeeSwarm and
BeeNiche.

## Run summary

The deterministic integrated run completed 24 control
steps at the configured 100 Hz boundary. The final
selected policy was `nurse_brood`, the final body speed was
0.004 m/s, the final body-frame energy budget was
23.999 J, and the mean wing power across the rollout was
58.291 mW. Dance-floor recruitment produced
168 follower events across the rollout.

The final comb occupancy fraction was 0.083, and the
brood-temperature error at the final step was
2.424 °C from the configured 34
°C target [@kronenberg1982colonial]. The run ended
with empirical odor label `geraniol` selected from the
registered odor templates, and an empirical-alignment score of
0.000.

## Witness figures

![Matplotlib BeeBody energy time series generated from simulation records; sidecar validation checks the raster, and the figure supports deterministic reduced-run energy accounting rather than calibrated honeybee energetics.](../figures/body_energy_timeseries.png){#fig:body_energy}

![Matplotlib BeeNiche comb-occupancy time series generated from simulation records; sidecar validation checks the raster, and the figure supports deterministic niche-kernel behavior rather than full hive ecology.](../figures/comb_fraction_timeseries.png){#fig:comb_fraction}

![Matplotlib BeeStack module contract coverage generated from module coverage records; sidecar validation checks the raster, and the figure supports implemented-contract coverage rather than scientific validation completeness.](../figures/module_contract_coverage.png){#fig:module_coverage}

## Artifact trace

The run summary is not a one-off console transcript. The values in this
section are written to `output/data/run_summary.json`, the per-step
records are written to `output/data/simulation_records.json`, and the
contract coverage witness is written to `output/data/module_coverage.json`.
The same pipeline writes `output/data/animation_manifest.json`,
`output/reports/beestack_integrity_review.md`, and the hydrated sections
under `output/manuscript/`. That trace makes the integrated run auditable:
if a figure or sentence changes, the corresponding JSON or report changes
with it.

## How to read these numbers

These are **reproducibility witnesses**, not biological validation
claims. They show that the complete five-module path can run
deterministically from a pinned seed
(`20260513`) while producing inspectable intermediate records,
figures, reports, and manuscript variables. Re-running the same seed
on the same code reproduces every number above to within numerical
precision; changing the seed changes the trajectory but not the
contract-validity of any artifact.

The empirical-alignment score should be read especially conservatively.
The current BeeBrain empirical layer projects available odor templates
into a reduced AL–MB–CX path; the alignment metric measures whether
the projected MB activity matches the expected template signature, not
whether the underlying neural model is biologically calibrated. A high
alignment score with the current kernel is a sanity check that the
template-bank pipeline is wired correctly; it is not a claim about
neural predictive validity. The full predictive validity claim lives
in the roadmap.

## What the run does *not* claim

The integrated run does not claim:

1. **Population-scale dynamics** — recruitment numbers come from the
   reduced communication kernel, not from a BEEHAVE-scale
   demographic engine.
2. **Calibrated biomechanics** — the energy and wing-power numbers
   come from the reduced energetics model, not from a measured
   honey-bee biomechanics dataset.
3. **Learned policy quality** — `nurse_brood` is the
   highest-scoring policy under the hand-calibrated
   active-inference-style scorer; it is not the output of a learned
   colony-optimal controller.
4. **Real-time thermoregulation accuracy** — the brood-temperature
   error number measures whether the kernel keeps the target band
   approximately, not whether the dynamics match real hive thermal
   response curves [@kronenberg1982colonial].

Naming the negatives is what makes the positive claims interesting:
the run is a *contract-valid whole-stack rollout that produces a
manuscript without fabrication*. That is the operational meaning of
"executable architecture" in this project.

## Cross-references to per-module results

Where the run touches a specific module, the relevant per-module
results section provides the depth: BeeBody for the energetics and rendering,
BeeBrain for the AL–MB–CX trace, BeeMind for the policy-score landscape,
BeeSwarm for the recruitment and contact pairs, and BeeNiche for the comb and
thermal traces. Empirical anchor data are summarized in "Empirical Results";
the research-suite
scorecards and known-gaps catalog are in "Research-Suite Results."
