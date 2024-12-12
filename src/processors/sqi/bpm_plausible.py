from src.processors.sqi.base import SQIBase

import pandas as pd

class SQIBpmPlausible(SQIBase):
    def compute(self, segment):
        """ Check for plausible BPM """
        max_bpm = 180
        min_bpm = 30
        
        # This should be a separate processing oepration - compute_ibi 
        # Select all beat peaks
        peaks = segment[segment['is_beat_peak'] == True].copy()
        peaks = peaks.sort_values(by=['group_id','timestamp_ms'])
        peaks['diff_ms'] = peaks.groupby('group_id')['timestamp_ms'].diff()
        mean_ibi = peaks.groupby('group_id')['diff_ms'].mean()
        
        bpm = 60000 / mean_ibi 
        
        if bpm < max_bpm and bpm > min_bpm:
            result = True
        else:
            result = False

        return result
