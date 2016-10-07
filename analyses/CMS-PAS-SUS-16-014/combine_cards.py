import os
import math
import sys
from ROOT import *

from optparse import OptionParser

methods = {'CLs': 'Asymptotic', 'PL': 'ProfileLikelihood', 'ML': 'MaxLikelihoodFit'}

parser = OptionParser()
parser.add_option('-b', action='store_true', dest='noX', default=False, help='Run in batch mode (no X11 windows)')
parser.add_option('--run', action='store_true', dest='run', default=False, help='Make RooStats workspace from combined datacard, then run fit')
parser.add_option("--dir", dest="dir", default="test", help="Directory containing SR datacards (output goes here as well)", metavar="dir")
parser.add_option("--M", dest="method", default="CLs", help="Fit method: CLs (asymptotic CLs limits), PL (obs. limit from profile likelihood), ML (maximum likelihood--best fit for signal strength)", metavar="dir")

(options, args) = parser.parse_args()


#########################################################################################################
#########################################################################################################
if __name__ == '__main__':

    # make sure directory exists, raise exception if it doesn't
	cdir = options.dir
    try:
        sr_cardnames = os.listdir(cdir)
    except OSError:
        raise
          
	command = 'combineCards.py ';
    # combine the signal region datacards
	for cn in sr_cardnames:
		if 'card_' in cn:
            command += " " + cdir+'/'+cn
    # combine the control region datacards
    cr_cardnames = os.listdir('CR')
    for cn in cr_cardnames:
		if 'card_' in cn:
            command += " " + cdir+'/'+cn
    # now combine them all into one text file
    command += " > "+cdir+'/allcards.txt'
	os.system(command);

	if options.run:

        combine_cmmd = "text2workspace.py %s/allcards.txt -o %s/allcards.root" % (cdir,cdir)
        os.system(combine_cmmd)
        if options.method in list(methods.keys()):
            combine_cmmd = "combine -M %s %s/allcards.root -n %s" % (methods[options.method], cdir, cdir);
            os.system(combine_cmmd);
        else:
            print: "Error: no valid fit method provided."

        
