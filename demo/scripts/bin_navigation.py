## tools for interpreting a collection of bins, figuring otu kinematic properties, etc.
from search_bin import SearchBin

def GetMinMaxNJets(bins): ## takes an array of bins, returns min, max njets
    min_njets = 3
    max_njets = int(0)
    for ibin in bins:
        sbin = SearchBin(ibin)
        if sbin.inj > max_njets:
            max_njets = sbin.inj
        if sbin.inj < min_njets:
            min_njets = sbin.inj
    return min_njets, max_njets

def GetMinMaxBTags(bins): ## takes an array of bins, returns min, max btags
    min_btags = 3
    max_btags = int(0)
    for ibin in bins:
        sbin = SearchBin(ibin)
        if sbin.inb > max_btags:
            max_btags = sbin.inb
        if sbin.inb < min_btags:
            min_btags = sbin.inb
    return min_btags, max_btags

def GetMinMaxMHT(bins): ## takes an array of bins, returns min, max mht
    min_mht = 3
    max_mht = int(0)
    for ibin in bins:
        sbin = SearchBin(ibin)
        if sbin.imht > max_mht:
            max_mht = sbin.imht
        if sbin.imht < min_mht:
            min_mht = sbin.imht
    return min_mht, max_mht

def GetMinMaxHT(bins): ## takes an array of bins, returns min, max ht
    min_ht = 2
    max_ht = int(0)
    for ibin in bins:
        sbin = SearchBin(ibin)
        if sbin.iht > max_ht:
            max_ht = sbin.iht
        if sbin.iht < min_ht:
            min_ht = sbin.iht
    return min_ht, max_ht

def GetMinMaxHTMHT(bins): ## takes an array of bins, returns min, max htmht
    min_htmht = 9
    max_htmht = int(0)
    for ibin in bins:
        sbin = SearchBin(ibin)
        if sbin.ihtmht > max_htmht:
            max_htmht = sbin.ihtmht
        if sbin.ihtmht < min_htmht:
            min_htmht = sbin.ihtmht
    return min_htmht, max_htmht

def GetNBJetsBins(minNJ=0, maxNJ=3, minHTMHT=0, maxHTMHT=3):
    
    bin_set = [[], [], [], []]
    for ibin in range(160):
        bini = SearchBin(ibin)
        if bini.inj < minNJ or bini.inj > maxNJ:
            continue
        if bini.ihtmht < minHTMHT or bini.ihtmht > maxHTMHT:
            continue
        bin_set[bini.inb].append(ibin)
    return bin_set

def GetNJetsBins(minNB=0, maxNB=3, minHTMHT=0, maxHTMHT=3):
    
    bin_set = [[], [], [], []]
    for ibin in range(160):
        bini = SearchBin(ibin)
        if bini.inb < minNB or bini.inb > maxNB:
            continue
        if bini.ihtmht < minHTMHT or bini.ihtmht > maxHTMHT:
            continue
        bin_set[bini.inj].append(ibin)
    return bin_set

def GetMHTBins(minNJ=0, maxNJ=3, minNB=0, maxNB=3, minHT=0, maxHT=2):

    bin_set = [[], [], [], []]
    for ibin in range(160):
        bini = SearchBin(ibin)
        if bini.inj < minNJ or bini.inj > maxNJ:
            continue
        if bini.inb < minNB or bini.inb > maxNB:
            continue
        if bini.iht < minHT or bini.iht > maxHT and not (maxHT==1 and bini.ihtmht==8):
            continue
        bin_set[bini.imht].append(ibin)
    return bin_set

def SumFromBinSubset(full_list, subset):
    total = 0.
    for ibin in range(len(full_list)):
        if ibin in subset:
            total += full_list[ibin]
    return total

minNJetsMap = {0:3, 1:5, 2:7, 3:9}
maxNJetsMap = {0:4, 1:6, 2:8}

def GetNJetsSelectionString(minNJets=0, maxNJets=3):
    if maxNJets ==3:
        return "N_{\\rm jet} \\geq %d" % minNJetsMap[minNJets]
    else:
        return "%d \\leq N_{\\rm jet} \\leq %d" % (minNJetsMap[minNJets], maxNJetsMap[maxNJets])

def GetNBJetsSelectionString(minNBJets=0, maxNBJets=3):
    if minNBJets==maxNBJets:
        return "N_{\\rm b-jet} = %d" % minNBJets
    elif maxNBJets==3:
        return "N_{\\rm b-jet} \\geq %d" % minNBJets
    else:
        return "%d \\leq N_{\\rm b-jet} \\leq %d" % (minNBJets, maxNBJets)

minHTMHTToMHTMap = {0:300, 1:300, 2:300, 3:350, 4:350, 5:350, 6:500, 7:500, 8:750, 9:750}
maxHTMHTToMHTMap = {0:350, 1:350, 2:350, 3:500, 4:500, 5:500, 6:750, 7:750}
    
def GetMHTSelectionString(minHTMHT=0, maxHTMHT=9):
    if maxHTMHT>=8:
        return "H_{T}^{\\rm miss} \\geq %d" % minHTMHTToMHTMap[minHTMHT]
    else:
        return "%d \\leq H_{T}^{\\rm miss} \\leq %d" % (minHTMHTToMHTMap[minHTMHT], maxHTMHTToMHTMap[maxHTMHT])

minHTMap = {0:300, 1:500, 2:1000}    
maxHTMap = {0:500, 1:1000}    
def GetHTSelectionString(minHT=0, maxHT=2, minHTMHT=0, maxHTMHT=9):
    if maxHT==2:
        if minHTMHT==8 and maxHTMHT==8:
            return '750 \\leq H_{T} \\leq 1500'
        elif minHTMHT==8:
            return 'H_{T} \\geq 750'
        elif minHTMHT==9:
            return 'H_{T} \\geq 1500'
        else:
            return 'H_{T} \\geq %d' % minHTMap[minHT]
    else:
        return "%d \\leq H_{T} \\leq %d" % (minHTMap[minHT], maxHTMap[maxHT])
