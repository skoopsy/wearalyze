class BasicBiomarkers:
    def __init__(self, data):
        self.data = data.copy()
    
    def compute_ibi(self):
        """
        Computes inter-beat-interval (IBI) for beats within the same grouping
        This mitigates calculating an IBI from beats that may be sequential via the 
        index but not temporally due to data filtering/segmentation/appending
        
        Note: IBI of the first beat will be NaN!
        The IBIs will be accessed via: data[data['is_beat_peak'] == true]['ibi_ms']

        """
        # Get the peak rows and calc ibis
        peaks = self.data.loc[self.data['is_beat_peak'] == True].copy()
        peaks = peaks.sort_values(by=['group_id','timestamp_ms'])
        peaks['diff_ms'] = peaks.groupby('group_id')['timestamp_ms'].diff()
        
        # add an ibi column into the input df and set ibis at is_beat_peak == True idx
        self.data['ibi_ms'] = None
        self.data.loc[peaks.index, 'ibi_ms'] = peaks['diff_ms']
        
        return self.data
    
    def compute_group_ibi_stats(self):
        # Filter to get just the peaks
        peaks = self.data.loc[self.data['is_beat_peak'], ['group_id','ibi_ms']]

        # Compute max and min per group
        group_stats = peaks.groupby('group_id')['ibi_ms'].agg(['min','max'])

        # Map results back to df
        self.data['ibi_min_group'] = self.data['group_id'].map(group_stats['min'])
        self.data['ibi_max_group'] = self.data['group_id'].map(group_stats['max'])
  
        return self.data

    def compute_bpm_from_ibi_group(self):
        """
        Computes a mean Beats Per Minute (BPM) based on the IBI
        of number of beats fed in
        """
        # Get slice of the data and organise it
        peaks = self.data[self.data['is_beat_peak'] == True].copy()
        peaks = peaks.sort_values(by=['group_id','global_beat_index'])
        
        # Calc bpm
        group_bpm = 60000 / peaks.groupby('group_id')['ibi_ms'].mean() 
        
        # Add group bpm into input df via mapping the values
        self.data['group_bpm'] = self.data['group_id'].map(group_bpm)
        
        return self.data

    def compute_bpm_from_ibi(self):
        #NOT WORKING 
        # Get slice of the data and organise it
        peaks = self.data[self.data['is_beat_peak'] == True].copy()
        peaks = peaks.sort_values(by=['group_id','global_beat_index'])
        
        # Calc bpm
        peaks['instant_bpm'] = 60000 / peaks['ibi_ms'] 
        bpm_mapping = peaks['instant_bpm'].to_dict()
 
        # Add group bpm into input df via mapping the values
        self.data['instant_bpm'] = self.data.index.map(bpm_mapping)
        
        return self.data
 
    def compute_bpm_from_total_time(self):
        """
        Compute a beats per minute (BPM) by taking the overall time, dividing it by the 
        number of beats and projecting that out to 1 minute.
        """
        pass
