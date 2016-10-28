## class for storing BG measurements, including central values and uncertainties
import numpy as np
from math import sqrt
from utils import SumOverBins, SumOverBinsInQuadrature

class BGEst:
    def __init__(self, CV=None, statUp=None, statDown=None, systUp=None, systDown=None): # standard constructor, a central value and 4 uncertainties -- can take floats, arrays (bins), or nothing
        self.set_vars(CV, statUp, statDown, systUp, systDown)
    
    def set_vars(self, CV, statUp, statDown, systUp, systDown):
        if CV == None: # default, no inputs, just sets up empty arrays
            self.CV = []
            self.statUp = []
            self.statDown = []
            self.systUp = []
            self.systDown = []
            self.errUp = []
            self.errDown = []
        elif type(CV) == float: # if you just give it one set of values, makes arrays of length 1 from these
            self.CV = [CV]
            self.statUp = [statUp]
            self.statDown = [statDown]
            self.systUp = [systUp]
            self.systDown = [systDown]
            self.errUp = [sqrt(statUp**2+systUp**2)]
            self.errDown = [sqrt(statDown**2+systDown**2)]
        else: #
            self.CV = CV
            self.statUp = statUp
            self.statDown = statDown
            self.systUp = systUp
            self.systDown = systDown
            self.errUp = [sqrt(stat**2+syst**2) for stat,syst in zip(statUp,systUp)]
            self.errDown = [sqrt(stat**2+syst**2) for stat,syst in zip(statDown,systDown)]

    def AddBin(self, CV, statUp, statDown, systUp, systDown): ## add a bin with a CV and uncertainties -- takes floats and appends to arrays
        self.CV.append(CV)
        self.statUp.append(statUp)
        self.statDown.append(statDown)
        self.systUp.append(systUp)
        self.systDown.append(systDown)

    def Print(self):
        print "Bin | CV + statUp - statDown + systUp - systDown"
        for ibin in range(len(self.CV)):
            print "%d | %3.2f + %3.2f - %3.2f + %3.2f - %3.2f" % (ibin, self.CV[ibin], self.statUp[ibin], self.statDown[ibin], self.systUp[ibin], self.systDown[ibin])

    def Sum(self):
        return sum(self.CV)

    def SumStatUp(self): # sum all uncertainties in quadrature, approx. that they're uncorrelated from bin-to-bin
        return sqrt(sum([x**2 for x in self.statUp]))

    def SumStatDown(self): # sum all uncertainties in quadrature, approx. that they're uncorrelated from bin-to-bin
        return sqrt(sum([x**2 for x in self.statDown]))

    def SumSystUp(self): # sum all uncertainties in quadrature, approx. that they're uncorrelated from bin-to-bin
        return sqrt(sum([x**2 for x in self.systUp]))

    def SumSystDown(self):
        return sqrt(sum([x**2 for x in self.systDown]))

    def SumErrUp(self):
        return sqrt(self.SumStatUp()**2+self.SumSystUp()**2)

    def SumErrDown(self):
        return sqrt(self.SumStatDown()**2+self.SumSystDown()**2)

    def FromBins(self, bin_array): # builds a new BG est from a set of bins
        newCV = SumOverBins(self.CV, bin_array)
        newstatUp = SumOverBinsInQuadrature(self.statUp, bin_array)
        newstatDown = SumOverBinsInQuadrature(self.statDown, bin_array)
        newsystUp = SumOverBinsInQuadrature(self.systUp, bin_array)
        newsystDown = SumOverBinsInQuadrature(self.systDown, bin_array)
        return BGEst(newCV, newstatUp, newstatDown, newsystUp, newsystDown)

    def FromBinsOfBins(self, outer_bin_array): # builds a new BG est from a set of lists of bins to aggregate (e.g. for 1D projections)
        newBG = BGEst()
        for bin_set in outer_bin_array:
            newCV = 0.
            newstatUp = 0.
            newstatDown = 0.
            newsystUp = 0.
            newsystDown = 0.
            for ibin in bin_set:
                ##print ibin, self.CV[ibin], self.statUp[ibin], self.statDown[ibin], self.systUp[ibin], self.systDown[ibin]
                newCV += self.CV[ibin]
                newstatUp += self.statUp[ibin]**2
                newstatDown += self.statDown[ibin]**2
                newsystUp += self.systUp[ibin]**2
                newsystDown += self.systDown[ibin]**2
            newBG.AddBin(newCV, sqrt(newstatUp), sqrt(newstatDown), sqrt(newsystUp), sqrt(newsystDown))
        return newBG
    
    def __add__(self, other):
        sumCV = list(np.array(self.CV) + np.array(other.CV))
        sumstatUp = []
        sumstatDown = []
        sumsystUp = []
        sumsystDown = []
        for ibin in range(len(sumCV)):
            sumstatUp.append(sqrt(self.statUp[ibin]**2 + other.statUp[ibin]**2))
            sumstatDown.append(sqrt(self.statDown[ibin]**2 + other.statDown[ibin]**2))
            sumsystUp.append(sqrt(self.systUp[ibin]**2 + other.systUp[ibin]**2))
            sumsystDown.append(sqrt(self.systDown[ibin]**2 + other.systDown[ibin]**2))
        return BGEst(sumCV, sumstatUp, sumstatDown, sumsystUp, sumsystDown)
