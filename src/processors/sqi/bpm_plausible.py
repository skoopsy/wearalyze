from src.processors.sqi.base import SQIBase

import pandas as pd

class SQIBpmPlausible(SQIBase):
    def compute(self, data):
        """ Check for plausible BPM """
        max_bpm = 180
        min_bpm = 30
        bpm_type = 'group_bpm'
        bpm = data.drop_duplicates(subset=['group_id','group_bpm'])['group_bpm']
        breakpoint()
        #data['sqi_bpm_plausible'] = bpm.apply(self.bpm_check)
        data['sqi_bpm_plausible'] = data.apply(
            lambda row: self.bpm_check(row, max_bpm, min_bpm), axis=1
        )

        breakpoint()
        return result

    def bpm_check(self, row, max_bpm, min_bpm):
        return row['group_bpm'] < max_bpm and row['group_bpm']>min_bpm
