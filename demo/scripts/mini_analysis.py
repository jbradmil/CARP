import MySQLdb as mdb
import os
import sys
import numpy as np
from math import sqrt
from utils import ensure_dir
from bg_est import BGEst

lumi = 12902.808    


    
## def get_optimal_asr(hsig, sumBG): #, 

##     Qs = {}
##     for ibin in range(hsig.GetNbinsX()):
##         Qs[ibin+1] = GetQ(hsig.GetBinContent(ibin+1), sumBG.hCV.GetBinContent(ibin+1))
##         #print("Bin %d: S = %3.2f, B = %3.2f -- Q = %3.2f" % (ibin+1, hsig.GetBinContent(ibin+1), hbg.GetBinContent(ibin+1), GetQ(hsig.GetBinContent(ibin+1), hbg.GetBinContent(ibin+1))))
##     best_bins = []
##     for ibin in sorted(Qs, key=Qs.get, reverse=True): #sorted(Qs.items(), key=operator.itemgetter(1), reverse=True):
##         if hsig.GetBinContent(ibin) >= 0.01: ## only look at bins with at least a hint of signal --- speed things up
##             best_bins.append(ibin)
##     # max_asr_Q = 0.0
##     max_signif = 0.
##     Nsig = 0.
##     Nbg = 0.
##     err_bg_up = 0.
##     err_bg_down = 0.
##     asr_bins = []
##     for ibin in best_bins:
##         Nsig_new = Nsig + hsig.GetBinContent(ibin)
##         Nbg_new = Nbg+sumBG.hCV.GetBinContent(ibin)
##         ## approximate that uncertainties are uncorrelated from bin-to-bin -- true if stats dominate
##         err_bg_up_new = sqrt(err_bg_up**2+sumBG.hStatUp.GetBinContent(ibin)**2+sumBG.hSystUp.GetBinContent(ibin)**2)
##         err_bg_down_new = sqrt(err_bg_down**2+sumBG.hStatDown.GetBinContent(ibin)**2+sumBG.hSystDown.GetBinContent(ibin)**2)
##         signif = GetSignificance(Nsig_new, Nbg_new, err_bg_up_new, err_bg_down_new)
##         if signif < 0.:
##             break
##         if signif > max_signif:
##             Nsig = Nsig_new
##             Nbg = Nbg_new
##             err_bg_up = err_bg_up_new
##             err_bg_down = err_bg_down_new
##             max_signif = signif
##             asr_bins.append(ibin)
##             print("Adding Bin %d: S = %3.2f, B = %3.2f + %3.2f - %3.2f" % (ibin, hsig.GetBinContent(ibin), sumBG.hCV.GetBinContent(ibin),\
##                                                                            sqrt(sumBG.hStatUp.GetBinContent(ibin)**2+sumBG.hSystUp.GetBinContent(ibin)**2),\
##                                                                            sqrt(sumBG.hStatDown.GetBinContent(ibin)**2+sumBG.hSystDown.GetBinContent(ibin)**2)))
##             print("Max signif: %f (%3.2f, %3.2f + %3.2f - %3.2f)" % (max_signif, Nsig, Nbg, err_bg_up, err_bg_down))
##     print(asr_bins)
    
    ## best_bins = list(best_Qs.keys())
    ## print(best_bins)
        
if __name__ == "__main__": # to run from command line, specify an output directory and a signal model (name, mMom, mLSP) 
    import sys

    outdir = sys.argv[1]
    ensure_dir("output/"+outdir) # create output directory if needed

    username = sys.argv[5]

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
            znn.add_bin(float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]))
        ## get qcd background estimation
        qcd = BGEst()
        cur.execute("SELECT * FROM qcd")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            qcd.add_bin(float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]))
        ## get lost lepton and hadronic tau background estimations -- combine them into one (wtop)
        lostlep = BGEst()
        cur.execute("SELECT * FROM lostlep")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            lostlep.add_bin(float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]))
        hadtau = BGEst()
        cur.execute("SELECT * FROM hadtau")
        for i in range(cur.rowcount):
            row = cur.fetchone()
            hadtau.add_bin(float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]))
        # combine into one wtop BG, correlating stat err but not syst err
        wtop = BGEst([a+b for a,b in zip(lostlep.CV,hadtau.CV)],\
                     [a+b for a,b in zip(lostlep.statUp,hadtau.statUp)],\
                     [a+b for a,b in zip(lostlep.statDown,hadtau.statDown)],\
                     [sqrt(a**2+b**2) for a,b in zip(lostlep.systUp,hadtau.systUp)],\
                     [sqrt(a**2+b**2) for a,b in zip(lostlep.systDown,hadtau.systDown)])
        # finally, get the expected signal yields
        # identify the table and column
        signal_table = sys.argv[2]
        mMom = sys.argv[3]
        mLSP = sys.argv[4]
        signal_column = "_".join([signal_table, mMom, mLSP])
        signal = []
        cur.execute("SELECT %s FROM %s" % (signal_column, signal_table))
        for i in range(cur.rowcount):
            row = cur.fetchone()
            signal.append(float(row[0]))
        print signal
