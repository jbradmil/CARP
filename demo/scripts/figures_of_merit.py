## tools for calculating p-values and significances for an observed number of events given an expected number of events with a two-sided uncertainty

from math import fabs, exp, log, sqrt
from scipy.stats import norm
from numpy import random

## get simple figure of merit Q given expected number of signal events Nsig and expected number of background events Nbkg
## useful for fast approximation of expected discovery significance
def GetQ(Nsig, Nbkg):
    return 2*(sqrt(Nsig+Nbkg)-sqrt(Nbkg))

## get pull of an observation relative to an prediction with an uncertainty 
## pull = difference between expected and observed numbers of events, divided by gaussian apprixmation of uncertainty on expectation
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

## calculate p-value of an observation of Nobs events, given a prediction of Npred + err_pred_up - err_pred_down by throwing toys
## note: to calculate expected p-value from an expected number of signal and background events,, set Npred to N(background), Nobs to N(signal+background)
## this approach is general enough not to rely on the assumption that the data are gaussian-distributed
## model the expected number of events as a poisson distribution with a mean determined by convulting a known yield with an assymetric lognormal distibution of its uncertainties
def GetPValue(Nobs, Npred, err_pred_up, err_pred_down):
    ## guess how many toys we need to throw by calculating simple Q score:
    Q = GetQ(Nobs-Npred, Npred)
    approx_p = 1-norm.cdf(Q) # guess the p value from this approx significance
    if approx_p == 0.:
        approx_p = 0.0000001
    num_toys = round(100/approx_p) # want to see the outcome at least 100 times -- e.g. for 2 sigma, need 2000 toys
    if num_toys > 1000000: # for really low p-values, need lots more toys, but need to limit computing time
        num_toys = 1000000 # cutoff at 10e6
    Nbelow=0
    Nabove=0
    Nequal=0
    if err_pred_down>Npred:
        err_pred_down = Npred
        #print ("Down uncertainty ("+str(err_pred_down)+") has to be smaller than Npred ("+str(Npred)+")")
        #return -999.

    mu = 0.
    valG = 0.
    random.seed(12456)
    #while (min(Nbelow,Nabove)+Nequal)<min_toys and (Nbelow+Nequal+Nabove)<max_toys:
    while (Nbelow+Nequal+Nabove)<num_toys: 
        ## convolve expected bkg with log-normal
        mu = Npred
        valG = random.normal(0,1)
        if mu==0:
            mu = fabs(valG)*err_pred_up ## Apply 2-sided Gaussian uncertainty
        elif valG>=0:
            mu *= exp(valG*log(1+err_pred_up/Npred))
        elif err_pred_down<0.8*Npred:
            mu *= exp(-valG*log(1-err_pred_down/Npred))
        else:
            mu = max(0., mu + valG*err_pred_down)
        # Finding if toy above the observed yield
        valPois = random.poisson(mu)
        if valPois>Nobs:
            Nabove += 1
        elif valPois==Nobs:
            Nequal += 1
        else:
            Nbelow += 1

    ## special cases
    if Nabove+Nequal==0:
        pvalue = 1/max_toys
        print("No toys above or at Nobs="+str(Nobs)+" for Npred "+str(Npred)+" ("+str(err_pred_up)+"-"+str(err_pred_down)+"). Returning "+str(pvalue))
        return pvalue
    if Nbelow+Nequal==0:
        pvalue = 1-1/max_toys
        print("No toys below or at Nobs="+str(Nobs)+" for Npred "+str(Npred)+"+ ("+str(err_pred_up)+"-"+str(err_pred_down)+"). Returning "+str(pvalue))
        return pvalue
    return (Nabove+Nequal/2.)/(Nbelow+Nequal+Nabove)

# convert a pvalue to a one-sided significance using the inverse of the normal cumulative distribution function
def PValueToSignificance(pvalue):
    return norm.ppf(1-pvalue)

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
        print "pull = %3.2f (calculation took %f seconds)" % (GetPull(nobs, nexp, exp_err_up, exp_err_down), timer()-start)
        start = timer()
        pvalue = GetPValue(nobs, nexp, exp_err_up, exp_err_down)
        significance = PValueToSignificance(pvalue)
        print "p-value = %f, significance = %3.2f (calculation took %f seconds)" % (pvalue, significance, timer()-start)
    elif calc_type == "exp":
        print "Expected %3.2f + %3.2f - %3.2f background events and %3.2f signal events" % (nexp, exp_err_up, exp_err_down, nobs-nexp)
        start = timer()
        print "Q = 2*( sqrt(S+B) - sqrt(B) ) = %3.2f (calculation took %f seconds)" % (GetQ(nobs-nexp, nexp), timer()-start)
        start = timer()
        pvalue = GetPValue(nobs, nexp, exp_err_up, exp_err_down)
        significance = PValueToSignificance(pvalue)
        print "p-value = %f, significance = %3.2f (calculation took %f seconds)" % (pvalue, significance, timer()-start)
