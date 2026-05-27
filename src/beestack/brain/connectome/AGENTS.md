# connectome/ - BeeBrain structural wiring

Typed graph model and Honeybee Standard Brain VRML parsers for the honest
BeeBrain connectome stack.

## Modules

| File | Role |
| --- | --- |
| `graph.py` | `ConnectomeNode`, `ConnectomeEdge`, `BeeBrainConnectomeReport` |
| `structural_wiring.py` | `build_structural_connectome()`, `connectome_tiers_from_report()` |

## Output

Canonical artifact: `output/data/bee_brain_connectome.json` (structural
projectome tier; synaptic tier explicitly unavailable).

## Boundaries

- Structural edges cite HSB VRML assets and documented pathway semantics only.
- No fabricated synaptic adjacency.
