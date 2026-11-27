# Local manuscript rendering

`scripts/render_manuscript.py` reads geometry and document metadata from
`docs/manuscript/config.yaml`, invokes local Pandoc with citeproc and the
source-owned cross-reference filter, then runs XeLaTeX twice for stable links.
Author citations and figure references in Pandoc syntax. The pinned Template
uses the fragment below for its independent snapshot render.

The combined PDF and intermediate TeX stay under this repository's `output/`;
TeX/font caches stay under `.uv-cache/manuscript/`. The publication gate checks
the readable PDF against its exact source/data/figure render receipt. A passing
build is not visual or biological validation.


```latex
% Used by the pinned Template snapshot render.
\usepackage{listings}
\usepackage{amsthm}
\newtheorem{theorem}{Theorem}
\theoremstyle{remark}
\newtheorem{remark}{Remark}
\newtheorem{example}{Example}
```
