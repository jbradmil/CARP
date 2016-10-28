import os
from math import sqrt

def full_path(path):
    return os.path.realpath(os.path.abspath(os.path.expanduser(path)))

def ensure_dir(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

def SumOverBins(list_to_sum, selected_bins): ## given a list and a list of entries to combine, sum over those entries
    return sum(list_to_sum[x] for x in selected_bins)

def SumOverBinsInQuadrature(list_to_sum, selected_bins): ## given a list and a list of entries to combine, sum over those entries
    return sqrt(sum(list_to_sum[x]**2 for x in selected_bins))
