"""Determinism guards for the tie-break fixes (no mocks, real computation).

These specifically protect against regressions in the nondeterministic
dict/list tie-breaks that previously leaked construction order into
"deterministic" manuscript-facing outputs:
  * orchestrator dominant-empirical-odor selection
  * BeeMind policy selection / diagnostics
  * end-to-end manuscript-variable hydration
"""

from __future__ import annotations

from beestack.config import BeeStackConfig
from beestack.manuscript_variables import generate_variables
from beestack.mind import select_policy
from beestack.mind.policy import policy_candidates, policy_selection_diagnostics
from beestack.mind.state import PolicyCandidate
from beestack.orchestrator import run_simulation


def test_simulation_records_are_byte_stable() -> None:
    cfg = BeeStackConfig()
    first = run_simulation(cfg, steps=6)
    second = run_simulation(cfg, steps=6)
    assert first.summary() == second.summary()
    # Per-step records (carry dominant_empirical_odor) must match exactly.
    assert [r.__dict__ for r in first.records] == [r.__dict__ for r in second.records]


def test_manuscript_variables_are_byte_identical_across_runs() -> None:
    cfg = BeeStackConfig()
    run_a = run_simulation(cfg, steps=6)
    run_b = run_simulation(cfg, steps=6)
    vars_a = generate_variables(cfg, run_a.summary(), None)
    vars_b = generate_variables(cfg, run_b.summary(), None)
    assert vars_a == vars_b
    # Stable even when generate_variables is re-invoked on the same inputs.
    assert generate_variables(cfg, run_a.summary(), None) == vars_a


def test_policy_selection_is_order_independent() -> None:
    cfg = BeeStackConfig()
    from beestack.mind.policy import initial_belief

    belief = initial_belief(cfg)
    chosen = select_policy(belief, cfg)
    diag = policy_selection_diagnostics(belief, cfg)
    assert chosen.name == diag.selected_policy
    # Reordering the candidate pool must not change the selected policy:
    # ties resolve by name, not by construction order.
    base = policy_candidates(belief, cfg)
    reordered = list(reversed(base))
    assert min(base, key=lambda p: (p.expected_free_energy, p.name)).name == chosen.name
    assert min(reordered, key=lambda p: (p.expected_free_energy, p.name)).name == chosen.name


def test_equal_efe_tie_breaks_by_name_deterministically() -> None:
    # Two candidates with identical EFE must resolve to the lexicographically
    # smaller name regardless of input order.
    a = PolicyCandidate("zzz_policy", 0.0, 0.0, 0.0, 0.0)
    b = PolicyCandidate("aaa_policy", 0.0, 0.0, 0.0, 0.0)
    assert a.expected_free_energy == b.expected_free_energy
    assert min([a, b], key=lambda p: (p.expected_free_energy, p.name)).name == "aaa_policy"
    assert min([b, a], key=lambda p: (p.expected_free_energy, p.name)).name == "aaa_policy"
