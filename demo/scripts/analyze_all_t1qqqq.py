from mini_analysis import *
from t1qqqq_models import *
import json

def analyze_all_t1qqqq(outdir, username):


    mMoms = []
    mLSPs = []
    expSigs = []
    obsSigs = []

    nModels = 0
    for imodel in t1qqqq_models:
        nModels += 1
        mMom = int(imodel.split("_")[1])
        mLSP = int(imodel.split("_")[2])
        if mMom < 1600 and mLSP < 600:
            if nModels % 10 > 0: continue
        elif nModels % 6 == 0:                
            exp_sig, obs_sig = mini_analysis(outdir, 'T1qqqq', mMom, mLSP, username)
            mMoms.append(mMom)
            mLSPs.append(mLSP)
            expSigs.append(exp_sig)
            obsSigs.append(obs_sig)

    with open('output/'+outdir+'/summary.json', 'w') as f:
        json.dump({'mMom': mMoms, 'mLSP': mLSPs, 'expected significance': expSigs, 'observed significance': obsSigs}, f)
    

if __name__ == "__main__": # to run from command line, specify an output directory and a signal model (name, mMom, mLSP) 
    import sys
    analyze_all_t1qqqq(sys.argv[1], sys.argv[2])
