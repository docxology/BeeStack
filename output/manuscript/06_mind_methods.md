# BeeMind Methods

BeeMind represents the individual bee as a *bounded policy-selection system*.
It maintains a 32-dimensional belief state, temporal-polyethism
caste priors [@johnson2010temporal], an energy state, dance-derived patch
beliefs, and colony-need terms. Its default policy horizon is
10 steps, and candidate expansion is bounded so
deterministic tests can cover every branch.

## Beliefs and caste

The `BeliefState` packs a 32-component latent vector, a
caste tag (nurse, forager, guard, builder, fanner), an energy scalar,
and a small bag of patch beliefs derived from decoded dance vectors.
The caste prior shifts the policy-score weighting so the same physical
state can produce different "right" actions for different bees in the
colony — a feature directly motivated by temporal polyethism
[@johnson2010temporal; @menzel2012honey]. Caste transitions are gated
by age proxies and energy thresholds; they are deterministic under the
seed.

## Policy scoring

The current policy layer is **active-inference-style** rather than a
full generative model. Candidate policies are scored with explicit
pragmatic value (alignment with colony need), epistemic value (expected
information gain about patches and conspecifics), energy cost (the
metabolic price of the action), risk cost (predator and ambient stress
penalties), and caste prior. The scoring is in the spirit of the
free-energy framework [@friston2010free; @parr2017working] but
deliberately substitutes hand-calibrated witnesses for the learned
transition and observation models that a full active-inference agent
would require.

## Diagnostics

The diagnostic record produced at each policy step contains:

- the **selected policy** (e.g. `nurse_brood`, `forage_high_quality`);
- the **strongest competitor** and its score;
- the **policy margin** (selected − competitor);
- the current **belief energy** $E$ and **energy deficit**
  $\Delta E$;
- the **expected-free-energy** terms (pragmatic, epistemic, risk,
  caste, energy);
- the active **configuration bounds** so a reviewer can see whether
  the choice rests inside or against a configured constraint.

This transparency is the point of the kernel. It makes it possible to
verify that policy choice is deterministic under a seed, monotonic with
relevant configuration changes, finite, and serializable.

## Policy-landscape methods panel

The methods-analysis layer adds a Mind policy-landscape panel that
exposes candidate count, expected-free-energy range, selected-policy
margin, policy-switch count, and final energy. The figure is written to
`output/figures/methods/beemind_methods_policy_landscape.png`.

![Matplotlib/pandas BeeMind policy-landscape dashboard generated from MethodsAnalysisReport and policy diagnostics; sidecar validation checks the raster, and the figure supports finite reduced-kernel policy transparency rather than a learned biological generative model.](../figures/methods/beemind_methods_policy_landscape.png){#fig:mind_methods_policy}

## Fidelity boundary

BeeMind does not yet claim:

1. **Learned transition dynamics** — the current transition model is a
   small hand-coded forward simulator over the 10-step
   horizon, not a model fit to colony data.
2. **Recursive social inference** — policies treat other bees as
   sources of waggle/pheromone evidence, not as themselves
   policy-selecting agents.
3. **Calibrated observation likelihoods** — the mapping from
   `BrainState` to belief updates is structurally faithful (e.g. a
   high-confidence dance does shift patch beliefs) but the precise
   likelihood functions are not learned from data.

Each of those gaps is roadmap-tagged and can enter the kernel
through the same `BeliefState` and `Action` contracts. The architecture
deliberately keeps these gaps separable from the rest of the stack: a
learned generative BeeMind would replace `score_policies()` and the
inner forward simulator while leaving every other module untouched.

## Why active-inference-style rather than RL

The choice of an active-inference-style framing over a flat
reward-maximizing reinforcement-learning agent is intentional. Bees act
under strong homeostatic constraints (energy, temperature, brood
demand) and rich social information channels (dances, pheromones,
trophallaxis). A free-energy framing naturally combines pragmatic
("reach the goal"), epistemic ("learn about the patch"), and
constraint-respecting ("don't run out of energy") terms in a single
scalar, which makes policy choices auditable in a way that a learned
black-box policy would not be [@friston2010free; @parr2017working].
This makes BeeMind a *bounded, hand-calibrated decision witness*, not a
learned generative model — and the manuscript reports it as such.
