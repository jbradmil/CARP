from mini_analysis import *
from t1bbbb_models import *
import json

def analyze_all_t1bbbb(outdir, username):


    mMoms = []
    mLSPs = []
    expSigs = []
    obsSigs = []

    nModels = 0
    for imodel in t1bbbb_models:
        nModels += 1
        if nModels % 6 == 0:
            mMom = int(imodel.split("_")[1])
            mLSP = int(imodel.split("_")[2])
            exp_sig, obs_sig = mini_analysis(outdir, 'T1bbbb', mMom, mLSP, username)
            mMoms.append(mMom)
            mLSPs.append(mLSP)
            expSigs.append(exp_sig)
            obsSigs.append(obs_sig)

    with open('output/'+outdir+'/summary.json', 'w') as f:
        json.dump({'mMom': mMoms, 'mLSP': mLSPs, 'expected significance': expSigs, 'observed significance': obsSigs}, f)

    

if __name__ == "__main__": # to run from command line, specify an output directory and a signal model (name, mMom, mLSP) 
    import sys
    analyze_all_t1bbbb(sys.argv[1], sys.argv[2])
