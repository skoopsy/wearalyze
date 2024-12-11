from scipy.signal import cheby2, filtfilt
import pandas as pd
import numpy as np
from datetime import timedelta

class PPGPreProcessor:
    def __init__(self, data, config):
        self.data = data
        self.config = config

    def create_thresholded_sections(self):
        """Identify valid sections of data based on threshold."""
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'], unit='ms')
        threshold = self.config['ppg_preprocessing']['threshold']
        min_duration = self.config['ppg_preprocessing']['min_duration']
        max_length = 60000

        # Mark sections above threshold
        self.data['above_threshold'] = self.data['ppg'] > threshold
        
        self.data['section_id'] = (self.data['above_threshold'] != self.data['above_threshold'].shift()).cumsum()
         
        sections = [section_df for _, section_df in self.data[self.data['above_threshold']].groupby('section_id')]
        
        # Filter sections by duration
        valid_sections = []
        for section in sections:
            start_time = section['timestamp_ms'].iloc[0]
            end_time = section['timestamp_ms'].iloc[-1]
            duration = end_time - start_time

            #if duration >= timedelta(seconds=min_duration):
            if duration >= min_duration*1000: # converted from s to ms
                section['data_points'] = len(section)
                
                if len(section) > max_length:
                    for i in range(0, len(section), max_length):
                        subsection = section.iloc[i:i + max_length].copy()
                        valid_sections.append(subsection)
                        print(f"Created subsection with {len(subsection)} data points")
                else:
                    valid_sections.append(section)
        
        # Re-assign a new section_id after filtering out other sections
        for i, section_df in enumerate(valid_sections, start=1):
            section_df['section_id'] = i

        return valid_sections

    def filter_cheby2(self, sections):
        """
        Apply Chebyshev Type II filter to each section of input data
        
        This outputs the result in two ways:
         1. appendeds a new column to the input dataframe inplace called filtered_value
         2. Returns a new dataframe with the filtered_values and timestamp on their own.
        """

        sample_rate = self.config['filter']['sample_rate']
        lowcut = self.config['filter']['lowcut']
        highcut = self.config['filter']['highcut']
        order = self.config['filter']['order']
        nyquist = 0.5 * sample_rate

        b, a = cheby2(order, 20, [lowcut / nyquist, highcut / nyquist], btype='band')
        filtered_sections = []

        for section in sections:
            # Run filter in forward and reverse to correct any phase delay
            filtered_values = filtfilt(b, a, section['ppg'])
            section['filtered_value'] = filtered_values
            section = section[['timestamp_ms','filtered_value']]
            filtered_sections.append(section)

        return filtered_sections
