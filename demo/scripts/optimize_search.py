import numpy as np
from math import sqrt
from bg_est import BGEst
from figures_of_merit import *
from timeit import default_timer as timer

def optimize_search(signal, sumBG): 
    ## Step 2: Make best aggregate bin,
    ## optimize bin selection to design the most sensitive simple analysis
    totalS = sum(signal)
    totalB = sum(sumBG.CV)
    print("Total expected S / B = %f / %f = %f" % (totalS, totalB, totalS/totalB))
    print("Optimizing bin selection for maximum expected significance...")
    Qs = {}
    start = timer()
    for ibin in range(len(signal)):
        Q = GetQ(signal[ibin], sumBG.CV[ibin])
        if Q < 0.01:
            # negligible sensitivity, no chance of seeing signal, skip it and save time
            continue
        Qs[ibin] = Q
    best_bins = []
    # get indices of bins, ranked from best to worst
    for ibin in sorted(Qs, key=Qs.get, reverse=True): 
        best_bins.append(ibin)
    max_signif = 0.
    Nsig = 0.
    Nbg = 0.
    err_bg_up = 0.
    err_bg_down = 0.
    asr_bins = []
    ninsp = 0
    for ibin in best_bins:
        ninsp += 1 ## count how many we looked at
        Nsig_new = Nsig + signal[ibin]
        Nbg_new = Nbg+sumBG.CV[ibin]
        ##     approximate that uncertainties are uncorrelated from bin-to-bin -- true if stats dominate
        err_bg_up_new = sqrt(err_bg_up**2+sumBG.statUp[ibin]**2+sumBG.systUp[ibin]**2)
        err_bg_down_new = sqrt(err_bg_down**2+sumBG.statDown[ibin]**2+sumBG.systDown[ibin]**2)
        signif = PValueToSignificance(GetPValue(Nsig_new+Nbg_new, Nbg_new, err_bg_up_new, err_bg_down_new))
        if Qs[ibin] < Qs[best_bins[0]]/50. or (max_signif-signif) > 0.5:
            # if we're getting here, these bins probably don't matter anymore
            break
        if signif > max_signif:
            Nsig = Nsig_new
            Nbg = Nbg_new
            err_bg_up = err_bg_up_new
            err_bg_down = err_bg_down_new
            max_signif = signif
            asr_bins.append(ibin)
        if max_signif > 5.:
            print "Found a 5+ sigma bin combination, stopping here"
            break ## if we have 5-sigma discovery senstivity, that's good enough

    ## now we have the optimal set of bins -- let's run this analysis and make some interesting plots
    print("Optimization performed on "+ str(ninsp) + " bins in " + str(timer()-start) + " seconds.")
    print("These are the bins to combine:")
    print(asr_bins)

    return asr_bins, max_signif
