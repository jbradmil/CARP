from __future__ import print_function

import sys
import subprocess
import os
import errno
import fileinput
import multiprocessing
import stat
import glob
import shutil
import utils

def get_combine(base_dir):
    combine_dir = os.path.join(base_dir,"HiggsAnalysis","CombinedLimit")
    cur_dir = os.getcwd()
    if not os.path.isdir(combine_dir):
        subprocess.check_call(["git","clone","git@github.com:ald77/HiggsAnalysis-CombinedLimit",combine_dir,"-b","CARP"])
    else:
        os.chdir(combine_dir)
        try: subprocess.call(["git","pull"])
        finally: os.chdir(cur_dir)

def get_vdt(base_dir):
    vdt_dir = os.path.join(base_dir, "vdt")
    if not os.path.isdir(vdt_dir):
        subprocess.check_call(["git","clone","git@github.com:dpiparo/vdt",vdt_dir])

def build_vdt(base_dir):
    cwd = os.getcwd()
    vdt_dir = os.path.join(base_dir, "vdt")
    utils.ensure_dir(os.path.join(vdt_dir,"include","vdt"))
    for f in glob.glob(os.path.join(vdt_dir,"include","*.h")):
        shutil.copy(f, os.path.join(vdt_dir,"include","vdt"))

    os.chdir(vdt_dir)
    try:
        os.chdir(os.path.join(vdt_dir,"src"))
        os.chmod(os.path.join(vdt_dir,"src","signatures_generator.py"),
                 stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        subprocess.check_call(["./signatures_generator.py"])
        os.chdir(vdt_dir)
        subprocess.check_call(["g++","-shared",
                               "-I"+os.path.join(vdt_dir,"include","vdt"),
                               os.path.join(vdt_dir,"src","vdtMath_signatures.cc"),
                               "-o",os.path.join(vdt_dir,"lib","libvdt.so")])
    finally:
        os.chdir(cwd)

def check_for_boost(path):
    path = utils.full_path(path)
    for root,dirs,files in os.walk(path):
        if "program_options.hpp" in files:
            return os.path.dirname(os.path.dirname(root))

def find_boost(base_dir):
    # macOS
    loc = check_for_boost("/usr/local/Cellar/boost")
    if loc: return loc

    # CMS
    scram_arch = None
    try: scram_arch = os.environ["SCRAM_ARCH"]
    except KeyError: pass
    if scram_arch: loc = check_for_boost(os.path.join("/afs/cern.ch/cms/",scram_arch,"external"))
    if loc: return loc
    
    # Unix
    loc = check_for_boost("/usr/include")
    if loc: return loc
    loc = check_for_boost("/usr/local/include")
    if loc: return loc
    loc = check_for_boost("/opt/include")
    if loc: return loc
    loc = check_for_boost("/opt/local/include")
    if loc: return loc

    # Give up
    raise Exception("Could not find boost")

def build_combine(base_dir):
    cwd = os.getcwd()
    combine_dir = os.path.join(base_dir,"HiggsAnalysis","CombinedLimit")
    os.chdir(combine_dir)
    try:
        boost_dir = find_boost(base_dir)
        vdt_dir = os.path.join(base_dir, "vdt")
        subprocess.check_call(["make","-k","-j",str(multiprocessing.cpu_count()),
                               "BOOST="+boost_dir,"VDT="+vdt_dir,
                               "EXTERNAL_OPTS_BEGIN=-I$(VDT)/include",
                               "EXTERNAL_OPTS_END=-Wno-error -w -I"+base_dir,
                               "EXTERNAL_LIBS_BEGIN=-L$(VDT)",
                               "EXTERNAL_LIBS_END=-l MathMore"])
    finally:
        os.chdir(cwd)
    utils.ensure_dir(os.path.join(base_dir,"python","HiggsAnalysis"))
    try:
        os.symlink(os.path.join(combine_dir,"python"),
                   os.path.join(base_dir,"python","HiggsAnalysis","CombinedLimit"))
    except OSError as e:
        if e.errno == errno.EEXIST: pass
        else: raise

def write_rootrc(base_dir):
    path = ".:{}:{}\n".format(os.path.join("$(ROOTSYS)","lib"),
                              os.path.join(base_dir,"HiggsAnalysis","CombinedLimit","lib"))
    with open(os.path.join(base_dir, ".rootrc"), "w") as f:
        f.write("*.*.Root.DynamicPath: {}".format(path))
        f.write("*.Root.DynamicPath: {}".format(path))
        f.write("MacOS.*.Root.DynamicPath: {}".format(path))
        f.write("MacOS.Root.DynamicPath: {}".format(path))
        f.write("Unix.*.Root.DynamicPath: {}".format(path))
        f.write("Unix.Root.DynamicPath: {}".format(path))
        f.write("WinNT.*.Root.DynamicPath: {}".format(path))
        f.write("WinNT.Root.DynamicPath: {}".format(path))
        f.write("Vms.*.Root.DynamicPath: {}".format(path))
        f.write("Vms.Root.DynamicPath: {}".format(path))
            
def setup(base_dir):
    get_combine(base_dir)
    get_vdt(base_dir)

    build_vdt(base_dir)
    build_combine(base_dir)
    write_rootrc(base_dir)
