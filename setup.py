#! /usr/bin/env python

from __future__ import print_function

import subprocess
import os
import errno
import fileinput
import multiprocessing

def fullPath(path):
    return os.path.realpath(os.path.abspath(os.path.expanduser(path)))

def getCombine(base_dir):
    combine_dir = os.path.join(base_dir, "HiggsAnalysis/CombinedLimit")
    if not os.path.isdir(combine_dir):
        subprocess.check_call(["git","clone","git@github.com:cms-analysis/HiggsAnalysis-CombinedLimit",combine_dir])

def getBoost(base_dir):
    pass

def getVDT(base_dir):
    vdt_dir = os.path.join(base_dir, "vdt")
    if not os.path.isdir(vdt_dir):
        subprocess.check_call(["git","clone","git@github.com:dpiparo/vdt",vdt_dir])

def buildVDT(base_dir):
    cwd = os.getcwd()
    vdt_dir = os.path.join(base_dir, "vdt")
    os.chdir(vdt_dir)
    try:
        subprocess.check_call(["cmake","-DCMAKE_INSTALL_PREFIX="+vdt_dir,"."])
    except OSError as e:
        if e.errno == errno.ENOENT:
            raise Exception("cmake required to continue. Please install from https://cmake.org/")
        else:
            raise
    else:
        subprocess.check_call(["make"])
        subprocess.check_call(["make","install"])
    finally:
        os.chdir(cwd)

def findBoost(base_dir):
    return "/usr/local/Cellar/boost/1.61.0_1"

def fixMakefileImp(f, base_dir):
    last_line_defined_ccflags = False
    this_line_defines_ccflags = False
    this_line_comment_ccflags = False
    for line in f:
        out = line
        out = out.replace("@ln -sd", "@ln -s")
        out = out.replace("-fipa-pta", "")
        out = out.replace("LIBS = $(ROOTLIBS)","LIBS = -L$(VDT)/lib $(ROOTLIBS)")
        out = out.replace("CCFLAGS = -D STANDALONE $(ROOTCFLAGS)","CCFLAGS = -D STANDALONE -I$(VDT)/include $(ROOTCFLAGS)")
        last_line_defined_ccflags = this_line_defines_ccflags
        this_line_defines_ccflags = "CCFLAGS = " in line
        this_line_comment_ccflags = "# CMSSW CXXFLAGS" in line
        if last_line_defined_ccflags and this_line_comment_ccflags:
            print("CCFLAGS += -Wno-unused-command-line-argument -Wno-unknown-warning-option -I"+base_dir)
        print(out, end="")

def fixMakefile(base_dir):
    path = os.path.join(base_dir, "HiggsAnalysis/CombinedLimit/Makefile")
    try:
        with fileinput.FileInput(path, inplace=True) as f:
            fixMakefileImp(f, base_dir)
    except AttributeError as e:
        f = fileinput.FileInput(path, inplace=True)
        try: fixMakefileImp(f, base_dir)
        finally: f.close()

def buildCombine(base_dir):
    cwd = os.getcwd()
    combine_dir = os.path.join(base_dir, "HiggsAnalysis/CombinedLimit")
    os.chdir(combine_dir)
    boost_dir = findBoost(base_dir)
    vdt_dir = os.path.join(base_dir, "vdt")
    fixMakefile(base_dir)
    subprocess.check_call(["make","-k","-j",str(multiprocessing.cpu_count()),"BOOST="+boost_dir,"VDT="+vdt_dir])
    os.chdir(cwd)
            
def setup(base_dir):
    getCombine(base_dir)
    getBoost(base_dir)
    getVDT(base_dir)

    buildVDT(base_dir)
    buildCombine(base_dir)

if __name__ == "__main__":
    setup(os.path.dirname(fullPath(__file__)))
