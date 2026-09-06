# References {#sec:references}

Bibliography lives in [`references.bib`](references.bib) and is read by Pandoc during PDF render. The build pipeline invokes Pandoc with `--natbib`, so every `[@key]` citation in the manuscript is rewritten to the appropriate natbib LaTeX citation command and resolved against the bib file.
