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
from bin_navigation import *
from download_data import *
from optimize_search import *
from do_the_physics import *
import json


lumi = 12902.808    
    
        

def mini_analysis(outdir, model, mMom, mLSP, username):
    ## setup output directory
    outdir_full = "output/%s/%s_%d_%d" % (outdir, model, mMom, mLSP)
    ensure_dir("output/"+outdir) # create output directory if needed
    ensure_dir(outdir_full) # create output directory if needed
    
    ## Step 1: read the data in from SQL database   
    data_obs, wtop, znn, qcd, signal = download_data(model, mMom, mLSP, username)
    sumBG = wtop + znn + qcd

    ## Step 2: optimize bin selection to design the most sensitive simple analysis
    bins_to_combine, max_signif = optimize_search(signal, sumBG)
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

    do_the_physics(data_obs, wtop, znn, qcd, signal, bins_to_combine, outdir_full)
    # save the important outputs to a JSON file
    with open(outdir_full+'/summary.json', 'w') as f:
        json.dump({'mMom': mMom, 'mLSP': mLSP,\
                   'expected significance': max_signif, 'observed significance': PValueToSignificance(p_obs)}, f)
    

    ## prepare the LaTeX summary from templates
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


    
    
