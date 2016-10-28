import json
from plotter_1d import *
from bin_navigation import *

def do_the_physics(data_obs, wtop, znn, qcd, signal, bins_to_combine, outdir_full):
    ## now prepare 1D physics distributions from best bins
    min_njets, max_njets = GetMinMaxNJets(bins_to_combine)
    min_nbjets, max_nbjets = GetMinMaxBTags(bins_to_combine)
    min_htmht, max_htmht = GetMinMaxHTMHT(bins_to_combine)
    min_mht, max_mht = GetMinMaxMHT(bins_to_combine)
    min_ht, max_ht = GetMinMaxHT(bins_to_combine)

    print "Writing output to " + outdir_full
    make_njets_projection(outdir_full+"/njets_projection.pdf", data_obs, wtop, znn, qcd, signal, min_nbjets, max_nbjets, min_htmht, max_htmht, min_ht, max_ht)
    make_nbjets_projection(outdir_full+"/nbjets_projection.pdf", data_obs, wtop, znn, qcd, signal, min_njets, max_njets, min_htmht, max_htmht, min_ht, max_ht)
    make_mht_projection(outdir_full+"/mht_projection.pdf", data_obs, wtop, znn, qcd, signal, min_njets, max_njets, min_nbjets, max_nbjets, min_htmht, max_htmht, min_ht, max_ht)


