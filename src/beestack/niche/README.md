# BeeNiche

BeeNiche owns comb construction, thermal dynamics, and landscape coupling. The
reduced backend uses a small voxel grid but exposes replacement points for sparse
GPU grids, BEEHAVE population coupling, and Hiveopolis-style thermal validation.

`thermal_step` uses dimensionless per-step mixing coefficients, not per-second
heat-transfer rates. Passive cooling defaults to `niche.passive_cooling_rate`;
an explicit argument overrides it. The explicit scheme admits only finite,
nonnegative coefficients with `0.12 + passive + 0.03*fanning + regulation <= 1`,
where regulation applies if any cells are occupied. Unsupported combinations
raise before updating, rather than clipping temperatures. Sources are degrees C
per step.
