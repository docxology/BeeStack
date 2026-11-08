# connectome/

Typed BeeBrain connectome graph built from Honeybee Standard Brain structural
assets. See [`AGENTS.md`](AGENTS.md).

Documented pathways remain available as `schematic_pathway` edges without local
supporting assets; that graph has tier `schematic_only`, zero structural coverage
and no empirical structural availability. `supporting_assets` records actually
loaded HSB asset IDs. A pathway contributes structural coverage only when its
specific supporting VRML asset yielded names, once per pathway (not per drawn
edge). This projectome/geometry context is not measured synaptic connectivity.
VRML geometry and DEF/USE names are prefix-sampled through bounded member reads
(5 MB anatomy, 2 MB wiring); counts and bounds do not describe unread tails or
certify their CRC integrity.
