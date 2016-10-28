from mini_analysis import *
from t1tttt_models import *
import json

def analyze_all_t1tttt(outdir, username):


    mMoms = []
    mLSPs = []
    expSigs = []
    obsSigs = []

    for imodel in t1tttt_models:
        mMom = int(imodel.split("_")[1])
        mLSP = int(imodel.split("_")[2])
        exp_sig, obs_sig = mini_analysis(outdir, 'T1tttt', mMom, mLSP, username)
        mMoms.append(mMom)
        mLSPs.append(mLSP)
        expSigs.append(exp_sig)
        obsSigs.append(obs_sig)

    with open('output/'+outdir+'/summary.json', 'w') as f:
        json.dump({'mMom': mMoms, 'mLSP': mLSPs, 'expected significance': expSigs, 'observed significance': obsSigs}, f)
   

if __name__ == "__main__": # to run from command line, specify an output directory and a signal model (name, mMom, mLSP) 
    import sys
    analyze_all_t1tttt(sys.argv[1], sys.argv[2])
