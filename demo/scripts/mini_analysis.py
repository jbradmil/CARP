## Mini-analysis!
## See https://github.com/jbradmil/CARP/tree/demo/demo for more information!

import MySQLdb as mdb
import os
import sys
import numpy as np
from math import sqrt
from utils import ensure_dir
from bg_est import BGEst
from figures_of_merit import *
from timeit import default_timer as timer
from bin_navigation import *
from plotter_1d import *
import json


lumi = 12902.808    
    
def make_best_aggregate_bin(signal, sumBG): 
    ## Step 2: optimize bin selection to design the most sensitive simple analysis
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
        

def mini_analysis(outdir, model, mMom, mLSP, username):
    ## Step 1: read the data in from SQL database   
    outdir_full = "output/%s/%s_%d_%d" % (outdir, model, mMom, mLSP)
    ensure_dir("output/"+outdir) # create output directory if needed
    ensure_dir(outdir_full) # create output directory if needed

    ## now connect to the SQL database
    con = mdb.connect(host='localhost', user=username, db='ra2')
    with con:
        cur = con.cursor()
        ## get the observed data
        data_obs = []
        cur.execute("SELECT * FROM data_obs")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            data_obs.append(int(row[1]))
        ## get znn background estimation
        znn = BGEst()
        cur.execute("SELECT * FROM znn")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            znn.AddBin(float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]))
        ## get qcd background estimation
        qcd = BGEst()
        cur.execute("SELECT * FROM qcd")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            qcd.AddBin(float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]))
        ## get lost lepton and hadronic tau background estimations -- combine them into one (wtop)
        lostlep = BGEst()
        cur.execute("SELECT * FROM lostlep")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            lostlep.AddBin(float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]))
        hadtau = BGEst()
        cur.execute("SELECT * FROM hadtau")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            hadtau.AddBin(float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]))
        # combine into one wtop BG, correlating stat err but not syst err
        wtop = BGEst([a+b for a,b in zip(lostlep.CV,hadtau.CV)],\
                     [a+b for a,b in zip(lostlep.statUp,hadtau.statUp)],\
                     [a+b for a,b in zip(lostlep.statDown,hadtau.statDown)],\
                     [sqrt(a**2+b**2) for a,b in zip(lostlep.systUp,hadtau.systUp)],\
                     [sqrt(a**2+b**2) for a,b in zip(lostlep.systDown,hadtau.systDown)])
        # finally, get the expected signal yields
        # identify the table and column
        signal_table = model
        signal_column = "_".join([signal_table, str(mMom), str(mLSP)])
        signal = []
        cur.execute("SELECT %s FROM %s" % (signal_column, signal_table))
        for i in range(cur.rowcount):
            row = cur.fetchone()
            signal.append(float(row[0]))

    sumBG = wtop + znn + qcd

    ## Step 2: optimize bin selection to design the most sensitive simple analysis
    bins_to_combine, max_signif = make_best_aggregate_bin(signal, sumBG)
    ## get the yields again
    Nobs = SumOverBins(data_obs, bins_to_combine)
    Nsig = SumOverBins(signal, bins_to_combine)
    Nbg = SumOverBins(sumBG.CV, bins_to_combine)
    err_bg_up = SumOverBinsInQuadrature(sumBG.errUp, bins_to_combine)
    err_bg_down = SumOverBinsInQuadrature(sumBG.errDown, bins_to_combine)

    ## Step 3: decide which plots to make for physics intuition, make paper skeleton document
    
    ## run the pvalue calculators one more time to make the plots
    p_exp = GetPValue(Nsig+Nbg, Nbg, err_bg_up, err_bg_down, outdir_full+'/pvalue_exp.pdf', False)
    print("S+B, B, Exp. Sig. = %3.2f, %3.2f + %3.2f - %3.2f, %3.2f (p = %f)" % (Nsig+Nbg, Nbg, err_bg_up, err_bg_down, max_signif, p_exp))
    p_obs = GetPValue(Nobs, Nbg, err_bg_up, err_bg_down, outdir_full+'/pvalue_obs.pdf', True)
    print("Obs., Pred., Obs. Sig. = %3.2f, %3.2f + %3.2f - %3.2f, %3.2f (p = %f)" % (Nobs, Nbg, err_bg_up, err_bg_down, PValueToSignificance(p_obs), p_obs))

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

    # save the important outputs to a JSON file
    with open(outdir_full+'/summary.json', 'w') as f:
        json.dump({'mMom': mMom, 'mLSP': mLSP,\
                   'expected significance': max_signif, 'observed significance': PValueToSignificance(p_obs)}, f)

    ## now copy the LaTeX summary template to the output directory
    with open(outdir_full+'/summary.tex', 'w') as fout:
        ## copy preamble already saved in output directory
        with open('output/preamble_template.tex', 'r') as fpre:
            preamble = fpre.read()
        fout.write(preamble)
        fout.write('\\begin{itemize}\n')
        bins_string = ''
        for b in [i+1 for i in sorted(bins_to_combine)]:
            bins_string += str(b) + ', '
        bins_string = bins_string.rsplit(", ", 1)
        fout.write('\\item Bins to combine: %s\n' % bins_string[0])     
        fout.write('\\item Expected signal $=%3.2f$, expected background $=%3.2f^{+%3.2f}_{-%3.2f}$\n' % (Nsig, Nbg, err_bg_up, err_bg_down))
        fout.write('\\item $N_{\\rm obs}=%d$\n' % Nobs)
        fout.write('\\end{itemize}\n')
        if max_signif<5.:
            # if the significance was huge, we didn't make the plot, so don't write it to .tex
            with open('output/sig_template.tex', 'r') as fsig:
                sig_text = fsig.read()
            fout.write(sig_text)                        
        with open('output/1d_template.tex', 'r') as f1d:
            latex_1d = f1d.read()
        fout.write(latex_1d)
        fout.write('\\end{document}\n')
    ## it should compile if all the plots have been made successfully
                          
    ## return exp sig, obs sig so we can store them
    return max_signif, PValueToSignificance(p_obs)
## end of mini_analysis
        
if __name__ == "__main__":
    # to run from command line, specify an output directory and a signal model (name, mMom, mLSP) 
    import sys

    outdir = sys.argv[1]
    model = sys.argv[2]
    mMom = int(sys.argv[3])
    mLSP = int(sys.argv[4])
    # username needs to be the last argument, so I don't have to commit it to Git
    username = sys.argv[5]
    
    mini_analysis(outdir, model, mMom, mLSP, username)


    
    
