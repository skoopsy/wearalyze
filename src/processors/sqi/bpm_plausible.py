from src.processors.sqi.base import SQIBase

import pandas as pd

class SQIBpmPlausible(SQIBase):
    def compute(self, data):
        """ Check for plausible BPM """
        max_bpm = 180
        min_bpm = 30
        bpm_type = 'group_bpm'
        bpm = data.drop_duplicates(subset=['group_id','group_bpm'])['group_bpm']
        
        # BPM Check
        data['sqi_bpm_plausible'] = data.apply(
            lambda row: self.bpm_check(row, 'group_bpm',  max_bpm, min_bpm), axis=1
        )

        return data

    def bpm_check(self, row, col, max_bpm, min_bpm):
        """
        Check that the column value for input row is within the min and max limits
        """
        return row[col] < max_bpm and row[col]>min_bpm
