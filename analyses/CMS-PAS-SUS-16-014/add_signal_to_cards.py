## takes a histogram with bin-by-bin signal yields,
## adds signal to SR datacards

import os
import sys
import errno
from ROOT import TFile, TH1
from optparse import OptionParser

def replace_signal(infile, nsig):
    fin = open(infile,'r')
    outfile = infile.replace(options.indir, options.outdir)
    fout = open(outfile,'w')
    for line in fin:
        values = line.split(' ')
        if values[1]=='SIGNAL':
            fout.write(line.replace(values[1], str(round(nsig,5))))
        else:
            fout.write(line)

parser = OptionParser()
parser.add_option("-d", "--indir", dest="indir", default="SR", help="directory containing datacards to edit")
parser.add_option("-f", "--infile", dest="infile", default="", help="input root file with signal histogram")
parser.add_option("-s", "--hist", dest="hist", default="", help="input signal histogram stored in infile")
parser.add_option("-o", "--outdir", dest="outdir", default="test", help="directory for storing new S+B SR datacards")
(options, args) = parser.parse_args()

 # make output directory, if it doesn't exist
print "Saving new cards to %s" % options.outdir
try:
    os.makedirs(options.outdir)
except OSError as exception:
    if exception.errno != errno.EEXIST:
        raise

# open signal file
fsig = TFile.Open(options.infile,"read")
#fsig.ls()
 
# get histos
hsig = fsig.Get(options.hist)
#hsig.Print("all")

nbins = hsig.GetNbinsX()
ncards = len(os.listdir(options.indir))
if nbins==ncards:
    print "Looking for signal in %d bins" % int(nbins)
    for bin in xrange(nbins):
        # get signal from hist
        nsig = hsig.GetBinContent(bin+1)
        # open temlpate cards
        incard = "%s/card_signal%d.txt" % (options.indir, int(bin))
        # create new card, swap in signal
        replace_signal(incard, nsig)
        
else:
    print "Error: found %d bins in root file but %d datacards" % (int(nbins), int(ncards))

    
