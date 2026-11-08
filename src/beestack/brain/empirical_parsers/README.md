# empirical_parsers/

Focused loaders for empirical BeeBrain archives (panels, calcium, waggle,
antennal movement, anatomy). See [`AGENTS.md`](AGENTS.md).

All recursive ZIP readers share an `ArchiveBudget` across descendants and skip
irrelevant payloads before expansion. XLSX packages are preflighted before both
openpyxl and pandas: workbook relationships resolve the actual worksheet parts,
including noncanonical sheet locations, before declared dimensions, actual
cell/row coordinates and aggregate sheet rectangles are bounded. External,
traversal, ambiguous and unsupported worksheet relationships are rejected;
only the ordinary XLSX workbook part at `xl/workbook.xml` is supported. Coordinate
syntax is bounded before integer conversion and cannot exceed XLSX's 1,048,576
rows or 16,384 columns, even with larger configured limits. Default budgets are
100,000 rows, 4,096 columns, 5 million cells per sheet and 10 million per workbook.
Standalone workbook input is capped at 512 MB; expanded packages at 256 MB and
individual package members at 128 MB. Limits reject, never crop data.

Calcium intake accepts MATLAB v5 and fixed-width numeric/string HDF5 Paoli
schemas (`db.bee` or root `bee`, numeric four/five-dimensional arrays). HDF5
hard-link cycles, excessive depth/nodes, external/soft links and variable-length,
reference or compound dtypes are explicit policy failures, not missing data.
Logical storage plus float64/padding/stack materialization is checked before
scientific array conversion. Defaults are 4 GB logical/materialization budget,
depth 16 and 10,000 graph nodes/elements. MATLAB v5 compressed streams and nested
matrix dimensions are preflighted before SciPy loading. HDF5 signatures are
recognized at zero or any available power-of-two user-block boundary starting
at 512 bytes, without scanning unrelated offsets or using temporary files. HDF5
only materializes the supported `bee`, `fs`, `odors`, `glomeruli` fields after
graph preflight.

Corruption and policy rejections propagate. Only genuinely absent inputs produce
empty results; rejected containers must not become successful empty summaries.
