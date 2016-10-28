#!/usr/bin/python
## stores properties of bin, including links to possibly-correlated bins
from __future__ import division

class SearchBin:

    def __init__(self, binnum):
        self.set_vars(binnum)
        
    def set_vars(self, binnum):
        self.num = binnum
        self.inj = self.GetINJ()
        self.inb = self.GetINB()
        self.ihtmht = self.GetIHTMHT()
        self.imht = self.GetIMHT()
        self.iht = self.GetIHT()
        
    def GetINJ(self):
        INJ = (self.num) // 40
        return INJ

    def GetINB(self):
        INB = ((self.num) % 40) // 10
        return INB

    def GetIHTMHT(self):
        IHTMHT = ((self.num) % 40) % 10
        return IHTMHT
    
    def GetIMHT(self):
        if self.ihtmht < 0:
            return -1
        elif self.ihtmht < 3:
            return 0
        elif self.ihtmht < 6:
            return 1
        elif self.ihtmht < 8:
            return 2
        else:
            return 3
    
    def GetIHT(self):
        if self.ihtmht < 0:
            return -1
        elif self.ihtmht == 0 or self.ihtmht == 3: # 300 < HT < 500
            return 0
        elif self.ihtmht == 1 or self.ihtmht == 4 or self.ihtmht == 6: # 500 < HT < 1000
            return 1
        else: 
            return 2 # note: we're putting HTMHT Box 9 (MHT>750, 750<HT<1500) in the same HT range as the bins with HT > 1000
                     # we're also putting HTMHT Box 10 (MHT>750, HT>1500) in the same HT range as the bins with HT > 1000    
        
    def GetBinsWithSameNJets(self, minEQ=False): # if you set minEQ to true, returns bins with JNJ >= INJ
        if minEQ:
            same_njets = [bin for bin in range(160) if (bin) // 40 >= self.inj]
        else:
            same_njets = [bin for bin in range(160) if (bin) // 40 == self.inj]
        return same_njets

    def GetBinsWithSameNBJets(self, minEQ=False):
        if minEQ:
            same_nbjets = [bin for bin in range(160) if ((bin) % 40) // 10 >= self.inb]
        else:
            same_nbjets = [bin for bin in range(160) if ((bin) % 40) // 10 == self.inb]
        return same_nbjets

    def GetBinsWithSameHTMHT(self, minEQ=False):
        if minEQ:
            same_htmht = [bin for bin in range(160) if ((bin) % 40) % 10 >= self.ihtmht]
        else:
            same_htmht = [bin for bin in range(160) if ((bin) % 40) % 10 == self.ihtmht]
        return same_htmht

    def GetBinsWithSameMHT(self, minEQ=False):
        if minEQ:
            same_mht = [bin for bin in range(160) if SearchBin(bin).imht >= self.imht]
        else:
            same_mht = [bin for bin in range(160) if SearchBin(bin).imht == self.imht]
        return same_mht

    def GetBinsWithSameHT(self, minEQ=False):
        if minEQ:
            same_ht = [bin for bin in range(160) if SearchBin(bin).iht >= self.iht]
        else:
            same_ht = [bin for bin in range(160) if SearchBin(bin).iht == self.iht]
        return same_ht

    def Print(self):
        print("Search bin %d: INJ/INB/IHTMHT = %d/%d/%d" % (self.num, self.inj, self.inb, self.ihtmht) )
    
    @classmethod
    def GetBin(cls, mht, ht, njets, nbjets): # get event bin number from kinematic observables
        if mht < 300 or ht < 300 or njets < 3:
            return -1 ## not in any analysis bin

        # which interval in NJets ?
        # [3, 4]; [5,6]; [7,8] [9,inf)
        inj = 0
        if njets >= 5 and njets<=6:
            inj = 1
        elif njets >= 7 and njets<=8:
            inj = 2
        elif (njets>=9):
            inj = 3

        # which interval in mht?
        # [300, 350]; (350,500]; (500,750] (750,inf)
        imht = 0
        if mht > 350 and mht <= 500:
            imht = 1
        elif mht > 500 and mht <= 750:
            imht = 2
        elif mht > 750:
            imht = 3

        # which interval in htmht?
        ihtmht = 0
        if imht == 0:
            if ht > 300 and ht <= 500:
                ihtmht = 0
            elif ht > 500 and ht <= 1000:
                ihtmht = 1
            elif ht > 1000:
                ihtmht = 2
        elif imht == 1:
            if ht > 350 and ht <= 500:
                ihtmht = 3
            elif ht > 500 and ht <= 1000:
                ihtmht = 4
            elif ht > 1000:
                ihtmht = 5
            else:
                return -1 # throw away event if ht < mht
        elif imht == 2:
            if ht > 500 and ht <= 1000:
                ihtmht = 6
            elif ht > 1000:
                ihtmht = 7
            else:
                return -1 # throw away event if ht < mht
        elif imht == 3:
            if ht > 750 and ht <= 1500:
                ihtmht = 8
            elif ht > 1500:
                ihtmht = 9
            else:
                return -1 # throw away event if ht < mht
        else:
            return -1

        return cls(inj*40 + nbjets*10 + ihtmht)
