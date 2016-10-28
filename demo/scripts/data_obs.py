#!/usr/bin/python
## class for storing observed data histograms, including central values and poisson (gamma) uncertainties
from scipy.stats import gamma
alpha = 1 - 0.6827

class DataObs:

    def __init__(self, CV):
        self.set_vars(CV)
        
    def set_vars(self, CV):
        self.CV = CV
        self.errUp = [gamma.ppf(1 - alpha / 2, N + 1)-N for N in CV]
        self.errDown = [N-gamma.ppf(alpha / 2, N) if N>0. else 0. for N in CV]       
        

        
