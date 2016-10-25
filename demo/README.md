# RA2 2016 Multijet + MHT Analysis
This directory contains all the tools I use to integrate the RA2 teams's analysis contributions into a mostly-unified framework for interpreting results and understanding the strengths and weaknesses of the analysis. Scripts used to generate public plots, e.g., those in CMS-PAS-SUS-16-014 and the supplementary material, are commited to the [SCRA2BLE](https://github.com/nhanvtran/SCRA2BLE/tree/ICHEP2016/PubPlots "SCRA2BLE repository").

## Overview

The [inputs](./inputs/) directory contains root files containing the 160-bin histograms of the observed data, data-driven background estimates and their uncertainties, and the expected contribution from various signal models. The [scripts](./scripts/) directory contains all of the code needed to produce the plots. All scripts are intended to be run from the [PubPlots](./) directory. All plots and tables produced by these scripts should be written to the [output](./output/) directory. Reference copies of the plots and tables made for our ICHEP result are included [here](./output/reference/).

Any new aggregate search regions or sets (histograms) of aggregate search regions should be added to [agg_bins.py](./scripts/agg_bins.py), following the examples provided. Any new correlation model (e.g. correlating over the 'nbjets' dimension) should be added to [uncertainty.py](./scripts/uncertainty.py#L46) following the examples provided.

## Instructions

### Setup
This code should run on a system with Python >= 2.7 and ROOT 6.

```
git clone git@github.com:jbradmil/RA2016
cd RA2016
```

### Produce input histograms
These scripts will make all histograms and calculate relevant uncertainties for each of the backgrounds, the observed data, and several signal models and save them to ROOT files that will be loaded in the next step. This step also handles the combination of bins for aggregate search regions (including 1-D projections), as well as the (almost) full correlations between background systematics.

Before proceeding, make sure you're aware of any changes to the structure of the background inputs since the last top-up. Ensure that the background-filling scripts are updated accordingly. Add any new signal models you'd like to plot to [fill_signal_hists](./scripts/fill_signal_hists.py).

To make all background, signal, and observed data inputs, you can do 

```
python scripts/fill_all_inputs.py
```

After you've set the appropriate inputs [here](./scripts/fill_all_inputs.py).

You can also run on an individual background by doing (e.g.)

```
python scripts/fill_qcd_hists.py  inputs/bg_hists/qcd-bg-combine-input-12.9ifb-july28-nodashes.txt  qcd_hists.root 160
```

### Make plots and tables
You can make all of the prefit results plots and tables from SUS-16-014, as well as a few others, by doing
```
python scripts/make_all_pas_plots_and_tables.py  lostlep_hists.root hadtau_hists.root znn_hists.root qcd_hists.root data_hists.root signal_hists.root
```
assuming that those are the names of the histogram files that you created by running [fill_all_inputs](./scripts/fill_all_inputs.py) and that they are all located in this directory. The file [make_all_pas_plots_and_tables](./scripts/make_all_pas_plots_and_tables.py) contains examples of how to call the scripts to make each individual plot.
