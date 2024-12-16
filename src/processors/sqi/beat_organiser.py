import pandas as pd

class BeatOrganiser:
    def __init__(self, group_size: int):
        self.group_size = group_size

    def group_n_beats_list(self, beats):
        """
        Group beats into n-sized segments

        args:
            beats (list): List containing individual beat time series
        returns:
            n_beat_groups (list): List containing n beat time series
        """
        
        n_beat_groups = [
            pd.concat(beats[i : i + self.group_size])
            for i in range(0, len(beats), self.group_size)
        ]

        return n_beat_groups
    
    def group_n_beats_inplace(self, df: pd.DataFrame):
        """
        Group beats into n-sized segments from a DataFrame
        Each segment will contain beats across sections, preserving order
        Assigns a global beat id, and a n-beat group id.   
        """
        
        # Filter rows with valid beats
        valid_data = df.loc[df['beat'] != -1].copy()
        
        # Sort items
        valid_data = valid_data.sort_values(by=['section_id','beat']).reset_index(drop=True)

        # Assign global index based on trough occurance
        trough_mask = valid_data['is_beat_trough'] == True
        trough_indices = valid_data.index[trough_mask]
        
        valid_data['global_beat_index'] = -1

        for beat_num, (start_idx, end_idx) in enumerate(zip(trough_indices[:-1], trough_indices[1:])):
            valid_data.loc[start_idx:end_idx, 'global_beat_index'] = beat_num
            
        # Check a single beat is being id correctly - beat# 100
        #plt.plot(valid_data['filtered_value'][valid_data['global_beat_index'] == 100])
        
        # Calculate group IDs based on group_sie
        valid_data['group_id'] = valid_data['global_beat_index'] // self.group_size
        #TODO: Might not be these lines! 
        # Check for groups spanning sections
        #group_section_check = valid_data.groupby('group_id')['section_id'].nunique()
        # Mark groups with beats from multiple sections as invalid
        #invalid_groups = group_section_check[group_section_check > 1].index
        #valid_data.loc[valid_data['group_id'].isin(invalid_groups), 'group_id'] = -1
        
        return valid_data 
       
        # I think the issue is that vlid_beats is assigning a global beat index to each row, not each beat - each data point within each beat so that the grouping is grouping 10 data points not 10 beats. 

