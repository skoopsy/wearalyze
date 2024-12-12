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
    
    def group_n_beats_inplace(self, beats_df: pd.DataFrame):
        """
        Group beats into n-sized segments from a DataFrame
        Each segment will contain beats across sections, preserving order
        Assigns a global beat id, and a n-beat group id.   
        """
        
        # Filter rows with valid beats
        valid_beats = beats_df[beats_df['beat'] != -1].copy()

        # Sort items
        valid_beats.sort_values(by=['section_id','beat'])
        
        # Assign global index
        valid_beats['global_beat_index'] = range(len(valid_beats))
        
        # Calculate group IDs based on group_size
        valid_beats['group_id'] = valid_beats['global_beat_index'] // self.group_size

        # Check for groups spanning sections
        group_section_check = valid_beats.groupby('group_id')['section_id'].nunique()

        # Mark groups with beats from multiple sections as invalid
        invalid_groups = group_section_check[group_section_check > 1].index
        valid_beats.loc[valid_beats['group_id'].isin(invalid_groups), 'group_id'] = -1
        
        return valid_beats 
        

