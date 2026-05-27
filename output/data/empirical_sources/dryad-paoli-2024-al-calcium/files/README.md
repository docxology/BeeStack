# Honey bee antennal lobe calcium imaging

[https://doi.org/10.5061/dryad.qbzkh18sc](https://doi.org/10.5061/dryad.qbzkh18sc)

This database comprises the data used for the analysis in Paoli et al., eLife (2024). It provides a set of honey bee antennal lobe calcium imaging recordings for 8 bees exposed to 3 odorants for 20 trials.

## Description of the data and file structure

The database (**db**) is in the form of a MatLab structure comprising:

* **db.allmaps** (described in **db.allmaps_legend**) contains the average response maps (64x64 pixels) for each olfactory stimulus (3 odorants) for 8 bees.
* **db.odors** (described in **db.odor_legend**) contains the name of the odorants used for the stimulations
* **db.bee** (described in **db.bee_legend**) contains 8 cells (one for each bee). Each cell has dimensions glomeuli-by-odorant-by-trial-by-time. Time is from 3s before odor onset to 20 s after odor onset. Calcium signal is recorded as relative change with respect to the pre-stimulus baseline (deltaF/F)
* **db.fs** contains the acquisition frequency rate used for each bee
* **db.xy** contains the x and y coordinates on the response maps (**db.allmaps**) used to extract glomerular information
