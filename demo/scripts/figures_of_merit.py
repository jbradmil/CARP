## tools for calculating p-values and significances for an observed number of events
## given an expected number of events with a two-sided uncertainty

from math import fabs, exp, log, sqrt, floor
from scipy.stats import norm
import numpy as np

## get simple figure of merit Q given expected number of signal events Nsig and expected number of background events Nbkg
## useful for fast approximation of expected discovery significance
def GetQ(Nsig, Nbkg):
    return 2*(sqrt(Nsig+Nbkg)-sqrt(Nbkg))

## get pull of an observation relative to an prediction with an uncertainty 
## pull = difference between expected and observed numbers of events,
## divided by gaussian apprixmation of uncertainty on expectation
## useful for fast approximation of observed discovery significance
def GetPull(Nobs, Npred, err_pred_up, err_pred_down):
    pull = 0.
    Nobs = float(Nobs)
    if err_pred_up**2 + Npred <= 0.: ## protect against dividing by zero (pathological case)
        print "Error: expected background has no CV and no uncertainty, returning 999."
        return 999.
    elif Npred < Nobs: # obs high
        return (Nobs-Npred)/sqrt(err_pred_up**2 + Npred) 
    elif Nobs < Npred: # obs low
        return (Nobs-Npred)/sqrt(err_pred_down**2 + Npred)

## Calculate p-value of an observation of Nobs events,
## given a prediction of Npred + err_pred_up - err_pred_down by throwing toys.
## Note: to calculate expected p-value from an expected number of signal and background events,
## set Npred to N(background), Nobs to N(signal+background).
## This approach is general enough not to rely on the assumption that the data are gaussian-distributed.
## Model the expected number of events as a poisson distribution with a mean determined by
## convoluting a known yield with an assymetric lognormal distibution of its uncertainties.
def GetPValue(Nobs, Npred, err_pred_up, err_pred_down, plot_title=None, obs=True):
    ## calculate how many toys we need from desired precision
    precision = 0.03;
    min_toys = 1/(precision**2)
    max_toys = 3500000 # to save time, don't throw more than 3.5 million toys (enough for ~ 5 sigma)
    if Npred > 100. and (Nobs-Npred)/sqrt(Npred) > 10.: ## and if this looks like it's gonna be ~8 sigma, just default to a very small number
        print(str(Nobs-Npred)+"/sqrt("+str(Npred)+") is very large, defaulting to ~8 sigma")
        return 1e-16
    # these will count the number of toys at, above, or below the mu we specified
    Nbelow=0
    Nabove=0
    Nequal=0
    
    if err_pred_down>Npred: # protect against pathological case
        err_pred_down = Npred
    mu = 0.
    valG = 0.
    
    np.random.seed(12456)
    # if we're making plot, will save these
    mu_arr = []
    pois_arr = []
    pois_SB_arr = []
    pois_high_arr = []
    pois_low_arr = []
    while (min(Nbelow,Nabove)+Nequal)<min_toys and (Nbelow+Nequal+Nabove)<max_toys:
        ## convolve expected bkg with log-normal
        mu = Npred
        valG = np.random.normal(0,1)
        if mu==0: # p-value for mu of 0 is 0, smear this out with Gaussian uncertainty
            mu = fabs(valG)*err_pred_up
        elif valG>=0:
            # vary mu within upper lognormal uncertainty on bkg measurement
            mu *= exp(valG*log(1+err_pred_up/Npred)) 
        elif err_pred_down<0.8*Npred:
            # vary mu within lower lognormal uncertainty on bkg measurement
            mu *= exp(-valG*log(1-err_pred_down/Npred))
        else:
            mu = max(0., mu + valG*err_pred_down)
        # Now sample from poisson dist, check if toy above the observed yield
        valPois = np.random.poisson(mu)
        valPoisSB = np.random.poisson(mu+Nobs-Npred)
        if valPois>Nobs:
            Nabove += 1
        elif valPois==Nobs:
            Nequal += 1
        else:
            Nbelow += 1
            
        if plot_title != None: # save values if we want to plot this
            mu_arr.append(mu)
            pois_arr.append(valPois)
            pois_SB_arr.append(valPoisSB)
            if valPois>=Nobs:
                pois_high_arr.append(valPois)
            else:
                pois_low_arr.append(valPois)
            
    ## special cases -- when you didn't throw enough toys
    if Nabove+Nequal==0:
        pvalue = 1/float(max_toys)
        print("No toys above or at Nobs="+str(Nobs)+" for Npred "+str(Npred)+" (+"+str(err_pred_up)+"-"+str(err_pred_down)+"). Returning "+str(pvalue))
        return pvalue
    if Nbelow+Nequal==0:
        pvalue = 1-1/float(max_toys)
        print("No toys below or at Nobs="+str(Nobs)+" for Npred "+str(Npred)+"+ (+"+str(err_pred_up)+"-"+str(err_pred_down)+"). Returning "+str(pvalue))
        return pvalue

    ## otherwise, calculate pvalue
    pvalue = (Nabove+Nequal/2.)/(Nbelow+Nequal+Nabove)   
    if plot_title != None:
        MakePDFPlot(plot_title, Nobs, Npred, err_pred_up, err_pred_down, pvalue, pois_arr, pois_SB_arr, obs)
        
    return (Nabove+Nequal/2.)/(Nbelow+Nequal+Nabove)

# convert a pvalue to a one-sided significance using the inverse of the normal cumulative distribution function
def PValueToSignificance(pvalue):
    return norm.ppf(1-pvalue)

# convert a one-sided significance to a pvalue using the normal cumulative distribution function
def SignificanceToPValue(signif):
    return 1-norm.cdf(signif)

def MakePDFPlot(plot_title, Nobs, Npred, err_pred_up, err_pred_down, pvalue, pois_arr, pois_SB_arr, obs):
    import matplotlib.pyplot as plt
    signif = PValueToSignificance(pvalue)
    binwidth = 1 + (max(pois_arr)-min(pois_arr))/100# (max(pois_arr)-min(pois_arr))/10.
    bins = np.arange(min(pois_arr), max(pois_arr)+binwidth+0.0001, binwidth)
    cutoffbinindex=max(i for i,b in enumerate(bins) if b<=Nobs)
    if cutoffbinindex==len(bins)-1: pois_vhigh_arr=[]
    else: pois_vhigh_arr = [b for b in pois_arr if b>(bins[cutoffbinindex]+binwidth/2.)]
    hcolor = '#6699CC'
    if not obs:
        hcolor = '#669900'
    histhandler = plt.hist(pois_arr, facecolor='none', bins=bins, histtype='step', color=hcolor, linewidth=2, label = 'B-only')
    n, bins2, patches = histhandler
    ## draw a verticle line for Nobs
    temp = [i for i,b in enumerate(bins2) if Npred > b]
    if len(temp) > 0:
        exp_line_height = n[max(temp)]
    else:
        exp_line_height = n[0]
    partial_bin_height=n[cutoffbinindex]
    plt.plot([Npred, Npred], [0, exp_line_height], linestyle='--', color=hcolor)
    if Nobs>Npred:
        if len(pois_vhigh_arr)>0: 
            plt.hist(pois_vhigh_arr, fill=True, facecolor=hcolor, bins=bins, histtype='step', edgecolor=hcolor, linewidth=2)
        plt.fill_between([Nobs,bins2[cutoffbinindex]+binwidth],[partial_bin_height,partial_bin_height], edgecolor=hcolor, facecolor=hcolor)
    if not obs:
        SB = plt.hist(pois_SB_arr, facecolor='none', bins=bins, histtype='step', color='red', linewidth=2, label='S+B')
        sig_n, sig_bins, sig_patches = SB
        temp = [i for i,b in enumerate(sig_bins) if Nobs > b]
        if len(temp) > 0:
            exp_line_height_sig = sig_n[max(temp)]
        else:
            exp_line_height_sig = sig_n[0]
        plt.plot([Nobs, Nobs], [0, exp_line_height_sig], linestyle='--', color='red')
    plt.xlabel(r'$N$', fontsize=15)
    plt.ylabel(r'$\mathrm{Toys}$', fontsize=15)
    if obs:
#        plt.text(0.65, 0.9, r'$N_{\rm obs} = %d$' % (Nobs), fontsize=15, transform=plt.gca().transAxes)
        plt.text(bins2[cutoffbinindex]+binwidth, 1.05*partial_bin_height, r'$N_{\rm obs} = %d$' % (Nobs), fontsize=15)
#        plt.text(0.65, 0.83, r'$N_{\rm exp} = %3.2f^{+%3.2f}_{-%3.2f}$' % (Npred, err_pred_up, err_pred_down), fontsize=15, transform=plt.gca().transAxes)
        plt.text(0.8*Npred, 1.05*exp_line_height, r'$\mu_{B} = %3.2f^{+%3.2f}_{-%3.2f}$' % (Npred, err_pred_up, err_pred_down), fontsize=15, color ='#0033CC')
        plt.ylim(0, 1.15*exp_line_height)
        if Nobs>=Npred:
            plt.text(0.6, 0.95, r'$P_{\rm obs}(N\geq N_{\rm obs}|\mu=B)=%f$' % (pvalue), fontsize=13, transform=plt.gca().transAxes)
        else:
            plt.text(0.6, 0.95, r'$P_{\rm obs}(N\leq N_{\rm obs}|\mu=B)=%f$' % (1-pvalue), fontsize=13, transform=plt.gca().transAxes)        
        plt.text(0.84, 0.88, r'$(%3.2f\sigma)$' % (signif), fontsize=15, transform=plt.gca().transAxes)
        legend = plt.legend(numpoints=1, frameon=False, bbox_to_anchor=(0.25, 1.02, 1., .102), loc=3, ncol=2, borderaxespad=0.)
    else:
#        plt.text(0.65, 0.9, r'$N_{S+B} = %3.2f$' % (Nobs), fontsize=15, transform=plt.gca().transAxes)
        plt.text(0.9*Nobs, 1.05*exp_line_height_sig, r'$\mu_{S+B} = %3.2f$' % (Nobs), fontsize=15, color ='#CC0033')
#        plt.text(0.65, 0.83, r'$N_{B} = %3.2f^{+%3.2f}_{-%3.2f}$' % (Npred, err_pred_up, err_pred_down), fontsize=15, transform=plt.gca().transAxes)
        plt.ylim(0, 1.15*max(exp_line_height,exp_line_height_sig))
        plt.text(0.9*Npred, 1.05*exp_line_height, r'$\mu_{B} = %3.2f^{+%3.2f}_{-%3.2f}$' % (Npred, err_pred_up, err_pred_down), fontsize=15, color ='#006600')
        plt.text(0.57, 0.95, r'$P_{\rm exp}(N\geq N_{S+B}|\mu=B)=%f$' % (pvalue), fontsize=13, transform=plt.gca().transAxes)
        plt.text(0.84, 0.88, r'$(%3.2f\sigma)$' % (signif), fontsize=15, transform=plt.gca().transAxes)
        legend = plt.legend(numpoints=1, frameon=False, bbox_to_anchor=(0.25, 1.02, 1., .102), loc=3,\
                            ncol=2, borderaxespad=0.)
     
    plt.gca().set_ylim(bottom=0.)
    plt.savefig(plot_title)
    plt.close()

# to run from command line, give an observed data yield (or expected number of signal+bkg events), and expected bkg yield, and + and - uncertainties on the bkg
# this will print out a variety of figures of merit
if __name__ == "__main__":
    import sys
    from timeit import default_timer as timer

    nobs = float(sys.argv[1])
    nexp = float(sys.argv[2])
    exp_err_up = float(sys.argv[3])
    exp_err_down = float(sys.argv[4])
    calc_type = 'exp'
    if len(sys.argv)>5:
        calc_type = sys.argv[5]

    if calc_type == "obs":
        print "Expected %3.2f + %3.2f - %3.2f events, observed %3.2f" % (nexp, exp_err_up, exp_err_down, nobs)
        start = timer()
        print "Q = 2*( sqrt(Obs) - sqrt(Exp) ) = %3.2f (calculation took %f seconds)" % (GetQ(nobs-nexp, nexp), timer()-start)
        start = timer()
        pvalue = GetPValue(nobs, nexp, exp_err_up, exp_err_down, 'pvalue_obs.pdf', True)
        significance = PValueToSignificance(pvalue)
        print "p-value = %f, significance = %3.2f (calculation took %f seconds)" % (pvalue, significance, timer()-start)
    elif calc_type == "exp":
        print "Expected %3.2f + %3.2f - %3.2f background events and %3.2f signal events" % (nexp, exp_err_up, exp_err_down, nobs-nexp)
        start = timer()
        print "Q = 2*( sqrt(S+B) - sqrt(B) ) = %3.2f (calculation took %f seconds)" % (GetQ(nobs-nexp, nexp), timer()-start)
        start = timer()
        pvalue = GetPValue(nobs, nexp, exp_err_up, exp_err_down, 'pvalue_exp.pdf', False)
        significance = PValueToSignificance(pvalue)
        print "p-value = %f, significance = %3.2f (calculation took %f seconds)" % (pvalue, significance, timer()-start)
