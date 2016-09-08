# CMS Analysis Reinterpretation Package

The purpose of this software is provide a straightforward and relatively simple way to reinterpret the results of CMS BSM searches in the context of any model. For each CMS analysis contained in this package, one should be able to:

* Take a MC sample of a model, figure out how many events from this model land in each search region of the analysis.
* Combine that information with a full description of the SM backgrounds in each region, as measured by CMS, to produce full SIG+BG and BG-only likelihood functions combinining information from all search regions.
* Evaluate the compatibility of the CMS data with the SIG+BG and BG-only hypotheses adn determine an upper limit on the cross section of the model.
