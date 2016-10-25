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
        elif type(CV) == float: # if you just give it one set of values, makes arrays of length 1 from these
            self.CV = [CV]
            self.statUp = [statUp]
            self.statDown = [statDown]
            self.systUp = [systUp]
            self.systDown = [systDown]
        else: #
            self.CV = CV
            self.statUp = statUp
            self.statDown = statDown
            self.systUp = systUp
            self.systDown = systDown

    def add_bin(self, CV, statUp, statDown, systUp, systDown): ## add a bin with a CV and uncertainties -- takes floats and appends to arrays
        self.CV.append(CV)
        self.statUp.append(statUp)
        self.statDown.append(statDown)
        self.systUp.append(systUp)
        self.systDown.append(systDown)

    def Print(self):
        print "CV + statUp - statDown + systUp - systDown"
        for ibin in range(len(self.CV)):
            print "%3.2f + %3.2f - %3.2f + %3.2f - %3.2f" % (self.CV[ibin], self.statUp[ibin], self.statDown[ibin], self.systUp[ibin], self.systDown[ibin])
