#! /usr/bin/env python

from __future__ import print_function

import sys
import os
import argparse
import python.utils as utils

def append_path(var, path):
    if var in os.environ:
        os.environ[var] = "{}:{}".format(path, os.environ[var])
    else:
        os.environ[var] = path

def set_environment(base_dir):
    sys.path.extend([os.path.join(base_dir,"python")])

    append_path("PYTHONPATH", os.path.join(base_dir,"python"))

    lib_path = os.path.join(base_dir,"HiggsAnalysis","CombinedLimit","lib")
    append_path("LD_LIBRARY_PATH", lib_path)
    append_path("LIBPATH", lib_path)
    append_path("SHLIB_PATH", lib_path)
    append_path("DYLD_LIBRARY_PATH", lib_path)

    append_path("PATH",os.path.join(base_dir,"HiggsAnalysis","CombinedLimit","exe"))
    append_path("PATH",os.path.join(base_dir,"HiggsAnalysis","CombinedLimit","scripts"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "CMS Analysis Recasting Package",
                                     formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(metavar="command", dest="command",
                                       help = "Selects action to perform.")

    setup = subparsers.add_parser("setup", help="Do one-time, initial setup.")

    process = subparsers.add_parser("process", help="Evaluate sensitivity of a search to a particular signal.")
    process.add_argument("signal_file", help="ROOT file containing signal histogram.")
    process.add_argument("analysis_dir", help="Directory for a particular analysis' background model.")

    args = parser.parse_args()

    base_dir = os.path.dirname(utils.full_path(__file__))
    set_environment(base_dir)

    if args.command == "setup":
        import setup
        setup.setup(base_dir)
    elif args.command == "process":
        import process
        process.process(base_dir, args.signal_file, args.analysis_dir)
