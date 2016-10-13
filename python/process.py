from __future__ import print_function

import utils
import models

def process(base_dir, signal_file, analysis_dir):
    signal_file = utils.full_path(signal_file)
    analysis_dir = utils.full_path(analysis_dir)

    models.initialize(analysis_dir)
