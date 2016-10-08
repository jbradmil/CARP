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
    combine_dir = os.path.join(base_dir,"HiggsAnalysis","CombinedLimit")
    cur_dir = os.getcwd()
    if not os.path.isdir(combine_dir):
        subprocess.check_call(["git","clone","git@github.com:ald77/HiggsAnalysis-CombinedLimit",combine_dir,"-b","CARP"])
    else:
        os.chdir(combine_dir)
        try: subprocess.call(["git","pull"])
        finally: os.chdir(cur_dir)

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

def checkForBoost(path):
    path = fullPath(path)
    for root,dirs,files in os.walk(path):
        if "program_options.hpp" in files:
            return os.path.dirname(os.path.dirname(root))

def findBoost(base_dir):
    # macOS
    loc = checkForBoost("/usr/local/Cellar/boost")
    if loc: return loc

    # CMS
    scram_arch = None
    try: scram_arch = os.environ["SCRAM_ARCH"]
    except KeyError: pass
    if scram_arch: loc = checkForBoost(os.path.join("/afs/cern.ch/cms/",scram_arch,"external"))
    if loc: return loc
    
    # Unix
    loc = checkForBoost("/usr/include")
    if loc: return loc
    loc = checkForBoost("/usr/local/include")
    if loc: return loc
    loc = checkForBoost("/opt/include")
    if loc: return loc
    loc = checkForBoost("/opt/local/include")
    if loc: return loc

    # Give up
    raise Exception("Could not find boost")

def buildCombine(base_dir):
    cwd = os.getcwd()
    combine_dir = os.path.join(base_dir,"HiggsAnalysis","CombinedLimit")
    os.chdir(combine_dir)
    try:
        boost_dir = findBoost(base_dir)
        vdt_dir = os.path.join(base_dir, "vdt")
        subprocess.check_call(["make","-k","-j",str(multiprocessing.cpu_count()),
                               "BOOST="+boost_dir,"VDT="+vdt_dir,
                               "EXTERNAL_OPTS_BEGIN=-I$(VDT)/include",
                               "EXTERNAL_OPTS_END=-Wno-error -w -I"+base_dir,
                               "EXTERNAL_LIBS_BEGIN=-L$(VDT)",
                               "EXTERNAL_LIBS_END=-l MathMore"])
    finally:
        os.chdir(cwd)
            
def setup(base_dir):
    getCombine(base_dir)
    getVDT(base_dir)

    buildVDT(base_dir)
    buildCombine(base_dir)

if __name__ == "__main__":
    setup(os.path.dirname(fullPath(__file__)))
