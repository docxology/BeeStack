# beestack.digital_twin

Machine-readable readiness assessment for the full systems-biology honeybee digital-twin target.

This package does not implement the full twin. It names the biological scales, evidence tiers, validation datasets, required artifacts, and acceptance tests needed to move BeeStack from an evidence-typed scaffold toward a colony and population-of-colonies digital twin.

Primary API:

- `digital_twin_axis_catalog()` — requirement catalog.
- `assess_digital_twin_readiness()` — aggregate maturity review.
- `digital_twin_readiness_markdown()` — report renderer for `output/reports/digital_twin_readiness.md`.
