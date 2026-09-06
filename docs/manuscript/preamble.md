# LaTeX Preamble

Packages injected by the template PDF renderer (`infrastructure/rendering/_pdf_latex_helpers.py`).

```latex
% Document layout
\usepackage[margin=0.15in]{geometry}
\usepackage{float}
\usepackage{graphicx}

% Mathematics and units
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{booktabs}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage[binary-units]{siunitx}

% Cross-references and citations
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    allcolors=red
}
\usepackage[capitalise,noabbrev]{cleveref}
\usepackage{natbib}
```
