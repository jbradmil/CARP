import os
import json
import numpy as np
from scipy.interpolate import Rbf
import matplotlib.pyplot as plt
import numpy.ma as ma
from numpy.random import uniform, seed

def make_scan(datadir):
    mMoms = []
    mLSPs = []
    expSigs = []
    obsSigs = []
    
    for subdir, dirs, files in os.walk(datadir):
        for infile in files:
            if os.path.join(subdir, infile).endswith('.json'):
                with open(os.path.join(subdir, infile)) as json_in:
                    data = json.load(json_in)
                    mMoms.append(data['mMom'])
                    mLSPs.append(data['mLSP'])
                    expSigs.append(data['expected significance'])
                    obsSigs.append(data['observed significance'])

    ## print mMoms
    ## print mLSPs
    ## print expSigs
    ## print obsSigs

    xlabel = '$m_{\\tilde{g}}\;[\\mathrm{GeV}]$'
    if datadir.find('t2tt') >= 0:
        xlabel = '$m_{\\tilde{t}}\;[\\mathrm{GeV}]$'
    elif datadir.find('t2bb') >= 0:
        xlabel = '$m_{\\tilde{b}}\;[\\mathrm{GeV}]$'
    elif datadir.find('t2qq') >= 0:
        xlabel = '$m_{\\tilde{q}}\;[\\mathrm{GeV}]$' 

    # define grid.
    xi = np.linspace(min(mMoms), max(mMoms), 100)
    yi = np.linspace(min(mLSPs), max(mLSPs), 100)

    XI, YI = np.meshgrid(xi, yi)
    # grid the data.
    rbf = Rbf(mMoms, mLSPs, expSigs, epsilon=2)
    ZI = rbf(XI, YI)
    #CS = plt.contour(xi,yi,zi,15,linewidths=0.5,colors='k')
    CS = plt.pcolor(XI, YI, ZI, cmap=plt.cm.jet, vmin=0, vmax=5)
    kin_lims = xi
    if datadir.find('t1tttt') >= 0:
        kin_lims = xi-350
    elif datadir.find('t2tt') >= 0:
        kin_lims = xi-175
    plt.fill_between(xi,kin_lims,max(mLSPs),color='white')
    plt.colorbar(label='Expected significance') # draw colorbar
    plt.xlim(min(mMoms),max(mMoms))
    plt.xlabel(r'%s' % xlabel, fontsize=15)      
    plt.ylabel(r'$m_{\tilde{\chi}^0_1}\;[\mathrm{GeV}]$', fontsize=15)
    plt.ylim(min(mLSPs),max(mLSPs))
    plt.savefig(datadir+'/exp_vs_B_sig.pdf')
    plt.clf()

    rbf = Rbf(mMoms, mLSPs, obsSigs, epsilon=2)
    ZI = rbf(XI, YI)
    CS = plt.pcolor(XI, YI, ZI, cmap=plt.cm.seismic, vmin=-3, vmax=3)
    plt.fill_between(xi,kin_lims,max(mLSPs),color='white')
    plt.colorbar(label='Observed significance') # draw colorbar
    plt.xlim(min(mMoms),max(mMoms))
    plt.xlabel(r'%s' % xlabel, fontsize=15)      
    plt.ylabel(r'$m_{\tilde{\chi}^0_1}\;[\mathrm{GeV}]$', fontsize=15)
    plt.ylim(min(mLSPs),max(mLSPs))
    plt.savefig(datadir+'/obs_vs_B_sig.pdf')
    plt.clf()


if __name__ == "__main__": # to run from command line, specify an output directory and a signal model (name, mMom, mLSP) 
    import sys
    make_scan(sys.argv[1])
