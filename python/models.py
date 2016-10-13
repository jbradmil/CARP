from __future__ import print_function

import os
import glob
import subprocess
import fnmatch

def combine_cards(model_dir):
    base_dir = os.path.dirname(os.path.dirname(model_dir))
    datacards = []
    for root,dirs,files in os.walk(os.path.join(model_dir,"datacards")):
        for f in files:
            if fnmatch.fnmatch(f, "*.txt"):
                datacards.append(os.path.join(root, f))
    command = [os.path.join(base_dir,"HiggsAnalysis","CombinedLimit","scripts","combineCards.py")]
    command.extend(datacards)
    with open(os.path.join(model_dir, "combined_datacard.txt"), "wb") as f:
        subprocess.check_call(command, stdout=f)

def make_workspace(model_dir):
    base_dir = os.path.dirname(os.path.dirname(model_dir))
    command = [os.path.join(base_dir,"HiggsAnalysis","CombinedLimit","scripts","text2workspace.py"),
               os.path.join(model_dir,"combined_datacard.txt"),
               "-b","-o",os.path.join(model_dir,"workspace.root")]
    subprocess.check_call(command)

def initialize(model_dir):
    combine_cards(model_dir)
    make_workspace(model_dir)
