# scripts/ - BeeStack Orchestrators

Keep scripts thin:

- Import domain logic from `src/beestack/`.
- Perform I/O, plotting, JSON serialization, and manuscript hydration here.
- Do not add simulation equations or scientific policy logic directly in scripts.
- `analysis_pipeline.py` generates both static figures and module animations.
