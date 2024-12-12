class BasicBiomarkers:
    def __init__(self, data):
        self.data = data.copy()
    
    def compute_ibi(self):
        """
        Computes inter-beat-interval (IBI) for beats within the same grouping
        This mitigates calculating an IBI from beats that may be sequential via the 
        index but not temporally due to data filtering/segmentation/appending
        """
        breakpoint()
        # Get the peak rows and calc ibis
        peaks = self.data[self.data['is_beat_peak'] == True].copy()
        breakpoint()
        peaks = peaks.sort_values(by=['group_id','timestamp_ms'])
        breakpoint()
        peaks['diff_ms'] = peaks.groupby('group_id')['timestamp_ms'].diff()
        
        # add an ibi column back into the input df
        self.data['ibi_ms'] = None
        self.data.loc[peaks.index, 'ibi_ms'] = peaks['diff_ms']
        
        breakpoint()

        return self.data
    
    def compute_bpm_from_ibi(self):
        """
        Computes a mean Beats Per Minute (BPM) based on the IBI of number of beats fed in
        """
        pass
    
    def compute_bpm_from_total_time(self):
        """
        Compute a beats per minute (BPM) by taking the overall time, dividing it by the 
        number of beats and projecting that out to 1 minute.
        """
        pass
