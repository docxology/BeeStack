# Introduction

## Motivation: the colony as a coupled body–brain–mind–swarm–niche system

BeeStack begins from a demanding biological premise: a honey bee colony is
not just many insects in one space, but a *coupled body–brain–mind–swarm–niche
system* in which information flows continually across morphological,
neural, behavioural, social, and ecological scales. Flight aerodynamics
constrains what can be foraged, olfactory encoding constrains which odors
can be communicated, the waggle dance compresses spatial cognition into a
two-dimensional kinematic signal, temporal polyethism re-tiles the colony
labour pool every few days, collective thermoregulation maintains the
brood within a narrow $32$–$36$ \si{\degreeCelsius} band, and comb
construction structures the very arena in which all of the previous
processes occur [@seeley1989superorganism; @seeley2010honeybee;
@menzel2012honey]. Models that treat these processes in isolation lose
precisely what makes a colony a colony: the cross-scale closures.

The "superorganism" framing is useful here only if it becomes
operational. Seeley used the term to emphasize colony-level integration
rather than metaphor alone [@seeley1989superorganism], and later work on
collective decision-making shows that insect societies can be studied
with some of the same formal questions used for individual cognition:
speed-accuracy tradeoffs, evidence accumulation, feedback, error
amplification, and distributed control [@sasaki2018superorganisms].
BeeStack takes that literature seriously by avoiding a single privileged
level. The worker body matters because morphology changes the control
problem; the brain matters because sensory evidence is compressed and
transformed; the mind matters because an individual forager must choose
under uncertainty; the swarm matters because recruitment and inhibition
turn many imperfect choices into colony-level dynamics; and the niche
matters because comb, heat, weather, and forage define the action space
available to the colony.

## Five biological layers in the BeeStack specification

The BeeStack project specification [@friedman2026beestack] identifies five
layers. **BeeBody** owns morphology, physics, sensors, actions, and
energetic accounting at the level of an individual worker. **BeeBrain**
maps sensory state through antennal-lobe, mushroom-body, central-complex,
optic, and waggle-decoding circuits with explicit anchors to honey-bee
neuroanatomy [@rybak2010digital; @galizia1999glomerular] and
behaviorally-relevant signals [@menzel2001cognitive; @stone2017central;
@honkanen2019sky].
**BeeMind** supplies individual active-inference-style beliefs and
policies in the spirit of the free-energy framework [@friston2010free;
@parr2017working]. **BeeSwarm** models many agents sharing dances,
pheromones, and task pressures [@free1987pheromones;
@johnson2010temporal]. **BeeNiche** represents the constructed comb,
the thermal field, and the foraging landscape interface
[@johnson2009self; @kronenberg1982colonial].

## From specification to executable scaffold

The v0 codebase turns those five layers into tested contracts rather than
prose only. This is deliberately modest and structural: the initial
backend is deterministic and reduced, while the APIs are designed so that
higher-fidelity engines can replace individual modules without rewriting
the entire stack. Body and small-scene swarm rendering already run
through FlyBody/MuJoCo tasks; the brain layer is anchored to public
empirical sources; the mind, communication, and niche layers ship as
bounded reduced kernels with explicit diagnostics.

## The architectural challenge: locally plausible, mutually incompatible

The architectural challenge is not simply to add detail. A bee-shaped
renderer, an antennal-lobe dataset, an active-inference policy, and a
colony simulator can each be locally plausible while remaining mutually
incompatible. Connect them naively and the seams hide undeclared scale
mismatches, drift between units of time and energy, or duplicate
representations of the same biological variable. BeeStack therefore
treats contracts as **scientific infrastructure**. Observations, actions,
brain states, belief states, dance and pheromone records, and comb grids
are typed, finite, serializable, deterministic under a seed, and
documented with their fidelity level. Module replacement remains a
mechanical exercise: substitute the implementation, satisfy the
contract, keep the evidence trail intact.

This contract discipline also follows the broader reproducible-science
lesson that research objects include not only data but also the workflows,
software, and documentation that produce those data [@wilkinson2016fair].
BeeStack borrows the spirit of model-card reporting [@mitchell2019modelcards]
without pretending that a biological simulation is an ML benchmark: each
module has intended-use language, fidelity labels, validation criteria,
known gaps, and generated artifacts. The same restraint matters for closed-loop twin language. In biomedicine,
that label is normally reserved for data-integrating models that can be
updated against individual or system-specific observations
[@bjornsson2020digitaltwins].
BeeStack is not yet a closed-loop twin for a particular colony. It is a
research scaffold whose APIs, provenance records, and validation reports
make future colony-coupled work easier to audit.

## How this manuscript mirrors the philosophy

The manuscript mirrors that philosophy. Instead of presenting BeeStack as
one large opaque model, the sections below separate **scope and
contributions**, **system architecture and contracts**, **per-module
methods** (BeeBody, BeeBrain, BeeMind, BeeSwarm, BeeNiche),
**visualization and validation**, **integrated results**, **empirical
BeeBrain results**, **research-suite results**, **discussion**,
**limitations**, **roadmap**, **reproducibility**, and **ethics and data
provenance**.
That structure is intended to make it easy to replace one layer at a
time while preserving the evidentiary trail for the stack as a whole. It
also lets reviewers focus on the layer relevant to their expertise: a
biomechanicist can read the BeeBody methods without the dance-decoding
details of the BeeBrain methods, and a neuroethologist can read the BeeBrain
methods without committing to the BeeSwarm contact-physics arguments.

## Claim discipline

BeeStack's central methodological move is to make every claim carry its
evidence class. A claim about BeeBody walking or the multi-bee waggle
scene can cite strict FlyBody/MuJoCo render artifacts. A claim about
odor templates, anatomy inventories, or waggle-follower antennae can cite
downloaded and parsed BeeBrain data. A claim about policy selection,
task allocation, or thermal regulation must be framed as a reduced
validated-kernel claim unless and until a stricter external engine
or calibrated dataset is actually wired into the contract. This
discipline is not a rhetorical hedge; it is the mechanism that lets a
large modular system improve one layer at a time without reporting planned
capabilities as present-tense results.

## Reading guide

Readers who want a one-page mental model should start with the abstract
and "System Architecture and Contracts." Readers who want to reproduce the
run should jump to "Reproducibility." Readers evaluating fidelity claims
should read "Discussion" and "Limitations" before "Integrated Results" so
the fidelity tier
of each number is visible before the number itself.
