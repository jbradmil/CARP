## I wrote this script to put the SIGNAL placeholder in the datacards

import os
import sys
from optparse import OptionParser

def remove_signal(infile):
    fin = open(infile,'r')
    outfile = infile.replace('/card_', '/NEW/card_')
    fout = open(outfile,'w')
    for line in fin:
        values = line.split(' ')
        if values[0]=='rate':
            fout.write(line.replace(values[1], 'SIGNAL'))
        else:
            fout.write(line)

parser = OptionParser()
parser.add_option("-d", "--directory", dest="directory", default="", help="directory in which we will fix cards")
(options, args) = parser.parse_args()

for filename in os.listdir(options.directory):
    if filename.endswith(".txt"):
        print 'Fixing %s' % options.directory+filename
        remove_signal(options.directory+filename)
