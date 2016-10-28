#!/usr/bin/python
## get the two obs/exp ratio graphs :
## 1 -- the markers with statistical uncertainties from data
## 2 -- the bands around ratio = 1 (or 0) with BG estimation uncertainty

from bg_est import BGEst
from data_obs import DataObs


class ObsExpRatio:

    def __init__(self, data_obs, bg_pred):
        self.set_vars(data_obs, bg_pred)
        
    def set_vars(self, data_obs, bg_pred):
        self.data_obs = data_obs
        self.bg_pred = bg_pred
        self.markers_cv = [(data-bg)/bg if bg>0. else 99. for data,bg in zip(data_obs.CV, bg_pred.CV)]
        self.markers_errUp = [data/bg if bg>0. else 0.0001 for data,bg in zip(data_obs.errUp, bg_pred.CV)]
        self.markers_errDown = [data/bg if bg>0. else 0.0001 for data,bg in zip(data_obs.errDown, bg_pred.CV)]
        self.bands_errUp = [bg_eup/bg if bg>0. else 99. for bg_eup,bg in zip(bg_pred.errUp, bg_pred.CV)]
        self.bands_errDown = [bg_edown/bg if bg>0. else 0. for bg_edown,bg in zip(bg_pred.errDown, bg_pred.CV)]
