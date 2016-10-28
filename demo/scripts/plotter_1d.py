## makes the 1D distributions from a range of bins determined in the optimization step
## to-do: consolidate these 3 functions into 1?
from bin_navigation import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib.lines as mlines
from math import sqrt
from utils import *
from data_obs import DataObs
from obs_exp_ratio import ObsExpRatio

def make_njets_projection(plot_title, data_obs, wtop, znn, qcd, signal, minNB=0, maxNB=3, minHTMHT=0, maxHTMHT=9, minHT=0, maxHT=2):
    hist_bin_lists = GetNJetsBins(minNB, maxNB, minHTMHT, maxHTMHT)
   
    data_hist = DataObs([SumFromBinSubset(data_obs, hist_bin_lists[inj]) for inj in range(4)])
    signal_hist = [SumFromBinSubset(signal, hist_bin_lists[inj]) for inj in range(4)]
    wtop_hist = wtop.FromBinsOfBins(hist_bin_lists)
    znn_hist = znn.FromBinsOfBins(hist_bin_lists)
    qcd_hist = qcd.FromBinsOfBins(hist_bin_lists)
    sumBG_hist = wtop_hist + znn_hist + qcd_hist
    
    bin_centers = [3.5, 5.5, 7.5, 10.5]
    bin_widths = [2, 2, 2, 4]
    bin_edges=[c-w/2 for c,w in zip(bin_centers,bin_widths)]

    z_hist = np.array(sumBG_hist.CV)
    wt_hist = np.array(qcd_hist.CV)+np.array(wtop_hist.CV)

    data_errors = [[i for i in data_hist.errDown], [i for i in data_hist.errUp]]

    bg_err_heights = np.array(sumBG_hist.CV)-np.array(sumBG_hist.errDown)
    bg_err_bands = np.array(sumBG_hist.errUp)+np.array(sumBG_hist.errDown)

    ratio = ObsExpRatio(data_hist, sumBG_hist)
    ratio_markers_cv = ratio.markers_cv
    ratio_markers_errs = [ ratio.markers_errDown, ratio.markers_errUp ]

    fig=plt.figure()
    gs = gridspec.GridSpec(4,1)
    ax1 = fig.add_subplot(gs[0:3,:])
    ax2 = fig.add_subplot(gs[3,:])

    zh=ax1.bar(bin_edges,z_hist, width=bin_widths, color='#F90035', label=r'$Z\rightarrow\nu\bar{\nu}$')
    wth=ax1.bar(bin_edges,wt_hist, width=bin_widths, color='#67C8FF', label=r'$W/t\bar[t}$')
    qh=ax1.bar(bin_edges,qcd_hist.CV, width=bin_widths, color='#EEEB8D', label='QCD')
    errh=ax1.bar(bin_edges, bg_err_bands, width=bin_widths, bottom=bg_err_heights, edgecolor='black', color='none', hatch='//', label='BG uncert.', linewidth=0.0)
    sh=ax1.step(bin_edges+[12.5], signal_hist+[0.], color='blue', where='post', lw=3)
    dh=ax1.errorbar(bin_centers, data_hist.CV, yerr=data_errors, color='black', fmt='o', ms=7, label='Data')

    ## Apparently I need a proxy handle to add the signal to the legend...
    blue_line = mlines.Line2D([], [], color='blue', lw=3)

    ymax = max( max(np.array(data_hist.CV)+np.array(data_hist.errUp)), max(np.array(sumBG_hist.CV)+np.array(sumBG_hist.errUp)), max(signal_hist) )
    
    ax1.set_ylim([0, ymax*1.5])
    ax1.set_xlim([2.5,12.5])
    ax1.set_xticklabels([])
    ax1.legend([dh, zh, wth, qh, errh, blue_line], ['Data', r'$Z\rightarrow\nu\bar{\nu}$', r'$W/t\bar{t}$', 'QCD', 'BG uncert', 'Signal'], numpoints=1, frameon=False)
    ax1.set_ylabel(r'$\mathrm{Events}$', fontsize=15)
    ax1.yaxis.set_label_coords(-0.1, 0.9)

    ax1.text(0.73, 1.05, r"$\int\;\mathcal{L}\;dt=12.9\;\mathrm{fb}^{-1}$", fontsize=13, transform=ax1.transAxes)
    ax1.text(0.03, 0.9, r"$\mathrm{Selection}: \; %s,\;%s\;\mathrm{GeV},\;%s\;\mathrm{GeV}$"\
             % (GetNBJetsSelectionString(minNB, maxNB), GetMHTSelectionString(minHTMHT, maxHTMHT), GetHTSelectionString(minHT, maxHT, minHTMHT, maxHTMHT)),\
             fontsize=10, transform=ax1.transAxes)
    
    ax2.set_xlim([2.5,12.5])
    ax2.set_ylim([-1.5,1.5])
    ax2.set_xlabel(r'$N_{\rm jet}\; (p_{T} > 30\;\mathrm{GeV}$)', fontsize=15)
    ax2.xaxis.set_label_coords(0.9, -0.3)
    ax2.set_ylabel(r'$\frac{\rm Obs.-Exp.}{\rm Exp.}$', fontsize=20)
    errh=ax2.bar(bin_edges, np.array(ratio.bands_errDown)+np.array(ratio.bands_errUp), width=bin_widths, bottom=[0.-down_err for down_err in ratio.bands_errDown], edgecolor='black', color='none', hatch='//', label='BG uncert.', linewidth=0.0)
    rmh = ax2.errorbar(bin_centers, ratio_markers_cv, yerr=ratio_markers_errs, color='black', fmt='o', ms=7, label='Ratio')
    ax2.plot([2.5,12.5], [0,0], linestyle='--', color='black')

    plt.savefig(plot_title)
    plt.close()


def make_nbjets_projection(plot_title, data_obs, wtop, znn, qcd, signal, minNJ=0, maxNJ=3, minHTMHT=0, maxHTMHT=9, minHT=0, maxHT=2):
    hist_bin_lists = GetNBJetsBins(minNJ, maxNJ, minHTMHT, maxHTMHT)

    data_hist = DataObs([SumFromBinSubset(data_obs, hist_bin_lists[inb]) for inb in range(4)])
    signal_hist = [SumFromBinSubset(signal, hist_bin_lists[inb]) for inb in range(4)]
    wtop_hist = wtop.FromBinsOfBins(hist_bin_lists)
    znn_hist = znn.FromBinsOfBins(hist_bin_lists)
    qcd_hist = qcd.FromBinsOfBins(hist_bin_lists)
    sumBG_hist = wtop_hist + znn_hist + qcd_hist
    
    bin_centers = [i for i in range(4)]
    bin_widths = [1]*4
    bin_edges=[i - 0.5 for i in range(4)]

    z_hist = np.array(sumBG_hist.CV)
    wt_hist = np.array(qcd_hist.CV)+np.array(wtop_hist.CV)

    data_errors = [[i for i in data_hist.errDown], [i for i in data_hist.errUp]]

    bg_err_heights = np.array(sumBG_hist.CV)-np.array(sumBG_hist.errDown)
    bg_err_bands = np.array(sumBG_hist.errUp)+np.array(sumBG_hist.errDown)

    ratio = ObsExpRatio(data_hist, sumBG_hist)
    ratio_markers_cv = ratio.markers_cv
    ratio_markers_errs = [ ratio.markers_errDown, ratio.markers_errUp ]

    fig=plt.figure()
    gs = gridspec.GridSpec(4,1)
    ax1 = fig.add_subplot(gs[0:3,:])
    ax2 = fig.add_subplot(gs[3,:])

    zh=ax1.bar(bin_edges,z_hist, width=bin_widths, color='#F90035', label=r'$Z\rightarrow\nu\bar{\nu}$')
    wth=ax1.bar(bin_edges,wt_hist, width=bin_widths, color='#67C8FF', label=r'$W/t\bar[t}$')
    qh=ax1.bar(bin_edges,qcd_hist.CV, width=bin_widths, color='#EEEB8D', label='QCD')
    errh=ax1.bar(bin_edges, bg_err_bands, width=bin_widths, bottom=bg_err_heights, edgecolor='black', color='none', hatch='//', label='BG uncert.', linewidth=0.0)
    sh=ax1.step(bin_edges+[3.5], signal_hist+[0.], color='blue', where='post', lw=3)
    dh=ax1.errorbar(bin_centers, data_hist.CV, yerr=data_errors, color='black', fmt='o', ms=7, label='Data')

    ## Apparently I need a proxy handle to add the signal to the legend...
    blue_line = mlines.Line2D([], [], color='blue', lw=3)

    ymax = max( max(np.array(data_hist.CV)+np.array(data_hist.errUp)), max(np.array(sumBG_hist.CV)+np.array(sumBG_hist.errUp)), max(signal_hist) )
    
    ax1.set_ylim([0, ymax*1.5])
    ax1.set_xlim([-0.5, 3.5])
    ax1.set_xticklabels([])
    ax1.legend([dh, zh, wth, qh, errh, blue_line], ['Data', r'$Z\rightarrow\nu\bar{\nu}$', r'$W/t\bar{t}$', 'QCD', 'BG uncert', 'Signal'], numpoints=1, frameon=False)
    ax1.set_ylabel(r'$\mathrm{Events}$', fontsize=15)
    ax1.yaxis.set_label_coords(-0.1, 0.9)

    ax1.text(0.73, 1.05, r"$\int\;\mathcal{L}\;dt=12.9\;\mathrm{fb}^{-1}$", fontsize=13, transform=ax1.transAxes)
    ax1.text(0.03, 0.9, r"$\mathrm{Selection}: \; %s,\;%s\;\mathrm{GeV},\;%s\;\mathrm{GeV}$"\
             % (GetNJetsSelectionString(minNJ, maxNJ), GetMHTSelectionString(minHTMHT, maxHTMHT), GetHTSelectionString(minHT, maxHT, minHTMHT, maxHTMHT)),\
             fontsize=10, transform=ax1.transAxes)
    
    ax2.set_xlim([-0.5, 3.5])
    ax2.set_ylim([-1.5,1.5])
    ax2.set_xlabel(r'$N_{\rm b-jet}\; (p_{T} > 30\;\mathrm{GeV})$', fontsize=15)
    ax2.xaxis.set_label_coords(0.9, -0.3)
    ax2.set_ylabel(r'$\frac{\rm Obs.-Exp.}{\rm Exp.}$', fontsize=20)
    errh=ax2.bar(bin_edges, np.array(ratio.bands_errDown)+np.array(ratio.bands_errUp), width=bin_widths, bottom=[0.-down_err for down_err in ratio.bands_errDown], edgecolor='black', color='none', hatch='//', label='BG uncert.', linewidth=0.0)
    rmh = ax2.errorbar(bin_centers, ratio_markers_cv, yerr=ratio_markers_errs, color='black', fmt='o', ms=7, label='Ratio')
    ax2.plot([-0.5,3.5], [0,0], linestyle='--', color='black')
    
    plt.savefig(plot_title)
    plt.close()

def make_mht_projection(plot_title, data_obs, wtop, znn, qcd, signal, minNJ=0, maxNJ=3, minNB=0, maxNB=3, minHTMHT=0, maxHTMHT=9, minHT=0, maxHT=2):
    hist_bin_lists = GetMHTBins(minNJ, maxNJ, minNB, maxNB, minHT, maxHT)
    
    data_hist = DataObs([SumFromBinSubset(data_obs, hist_bin_lists[imht]) for imht in range(4)])
    signal_hist = [SumFromBinSubset(signal, hist_bin_lists[imht]) for imht in range(4)]
    wtop_hist = wtop.FromBinsOfBins(hist_bin_lists)
    znn_hist = znn.FromBinsOfBins(hist_bin_lists)
    qcd_hist = qcd.FromBinsOfBins(hist_bin_lists)
    sumBG_hist = wtop_hist + znn_hist + qcd_hist
    
    bin_centers = [325, 425, 625, 900]
    bin_widths = [50, 150, 250, 300]
    bin_edges=[c-w/2 for c,w in zip(bin_centers,bin_widths)]

    z_hist = np.array(sumBG_hist.CV)
    wt_hist = np.array(qcd_hist.CV)+np.array(wtop_hist.CV)

    data_errors = [[i for i in data_hist.errDown], [i for i in data_hist.errUp]]

    bg_err_heights = np.array(sumBG_hist.CV)-np.array(sumBG_hist.errDown)
    bg_err_bands = np.array(sumBG_hist.errUp)+np.array(sumBG_hist.errDown)

    ratio = ObsExpRatio(data_hist, sumBG_hist)
    ratio_markers_cv = ratio.markers_cv
    ratio_markers_errs = [ ratio.markers_errDown, ratio.markers_errUp ]

    fig=plt.figure()
    gs = gridspec.GridSpec(4,1)
    ax1 = fig.add_subplot(gs[0:3,:])
    ax2 = fig.add_subplot(gs[3,:])

    zh=ax1.bar(bin_edges,z_hist, width=bin_widths, color='#F90035', label=r'$Z\rightarrow\nu\bar{\nu}$')
    wth=ax1.bar(bin_edges,wt_hist, width=bin_widths, color='#67C8FF', label=r'$W/t\bar[t}$')
    qh=ax1.bar(bin_edges,qcd_hist.CV, width=bin_widths, color='#EEEB8D', label='QCD')
    errh=ax1.bar(bin_edges, bg_err_bands, width=bin_widths, bottom=bg_err_heights, edgecolor='black', color='none', hatch='//', label='BG uncert.', linewidth=0.0)
    sh=ax1.step(bin_edges+[1050], signal_hist+[0.], color='blue', where='post', lw=3)
    dh=ax1.errorbar(bin_centers, data_hist.CV, yerr=data_errors, color='black', fmt='o', ms=7, label='Data')

    ## Apparently I need a proxy handle to add the signal to the legend...
    blue_line = mlines.Line2D([], [], color='blue', lw=3)

    ymax = max( max(np.array(data_hist.CV)+np.array(data_hist.errUp)), max(np.array(sumBG_hist.CV)+np.array(sumBG_hist.errUp)), max(signal_hist) )
    
    ax1.set_ylim([0, ymax*1.5])
    ax1.set_xlim([300, 1050])
    ax1.set_xticklabels([])
    ax1.legend([dh, zh, wth, qh, errh, blue_line], ['Data', r'$Z\rightarrow\nu\bar{\nu}$', r'$W/t\bar{t}$', 'QCD', 'BG uncert', 'Signal'], numpoints=1, frameon=False)
    ax1.set_ylabel(r'$\mathrm{Events}$', fontsize=15)
    ax1.yaxis.set_label_coords(-0.1, 0.9)

    ax1.text(0.73, 1.05, r"$\int\;\mathcal{L}\;dt=12.9\;\mathrm{fb}^{-1}$", fontsize=13, transform=ax1.transAxes)
    ax1.text(0.03, 0.9, r"$\mathrm{Selection}: \; %s,\;%s,\;%s\;\mathrm{GeV}$"\
             % (GetNJetsSelectionString(minNJ, maxNJ), GetNBJetsSelectionString(minNB, maxNB), GetHTSelectionString(minHT, maxHT, minHTMHT, maxHTMHT)),\
             fontsize=12, transform=ax1.transAxes)
    
    ax2.set_xlim([300, 1050])
    ax2.set_ylim([-1.5,1.5])
    ax2.set_xlabel(r'$H_{T}^{\rm miss}\;[\mathrm{GeV}]$', fontsize=15)
    ax2.xaxis.set_label_coords(0.9, -0.3)
    ax2.set_ylabel(r'$\frac{\rm Obs.-Exp.}{\rm Exp.}$', fontsize=20)
    errh=ax2.bar(bin_edges, np.array(ratio.bands_errDown)+np.array(ratio.bands_errUp), width=bin_widths, bottom=[0.-down_err for down_err in ratio.bands_errDown], edgecolor='black', color='none', hatch='//', label='BG uncert.', linewidth=0.0)
    rmh = ax2.errorbar(bin_centers, ratio_markers_cv, yerr=ratio_markers_errs, color='black', fmt='o', ms=7, label='Ratio')
    ax2.plot([300, 1050], [0,0], linestyle='--', color='black')
    
    plt.savefig(plot_title)
    plt.close()
