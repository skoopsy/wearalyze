from .compliance_check_factory import ComplianceCheckFactory

from scipy.signal import cheby2, filtfilt
import pandas as pd
import numpy as np
from datetime import timedelta

class PPGPreProcessor:
    def __init__(self, data, config):
        self.data = data
        self.config = config
        self.device = config['data_source']['device']

        # Factory to get device specific compliance thresholding methods
        self.compliance_check_method = ComplianceCheckFactory.get_check_method(self.device)
 
    def create_compliance_sections(self):
        """ 
        Delegates device compliance thresholding to device specific method
        """
    
        return self.compliance_check_method.create_compliance_sections(self.data, self.config)
         
    def compute_sample_freq(self, sections: list(), downsampling_factor=1):
        """
        Computess the sampling frequency of input data

        Note: there is downsmapling, but better to use resample()

        Args:
            sections (list of pd.DataFrame): sections of data thresholded for
                 compliance (may mitigate dynamic sampling issues)
            downsampling_factor (int): optional incase down sampling is required
        
        Return:
            int Computed sample frequency
            int Computed sample period (miliseconds)
            str Computed sample period string for pandas resampling
        """

        # Combine all sections into one for frequency calculation
        combined = pd.concat(sections, ignore_index = True)
        combined = combined.sort_values('timestamp_ms')

        # Calc intervals
        intervals_ms = combined['timestamp_ms'].diff().dropna()
        
        median_interval_ms = intervals_ms.median() # In ms

        freq = 1000.0 / median_interval_ms

        rounded_freq = round(freq)

        final_freq = rounded_freq / downsampling_factor

        interval_ms = 1000.0 / final_freq
        interval_ms = round(interval_ms, 3)
            
        interval_str = f'{int(interval_ms)}ms'
        
        print(f'[PPGPreProcessor] Sensor sample frequency (Raw): {final_freq} Hz')
        print(f'[PPGPreProcessor] Sensor sample period (Raw): {interval_str}')

        return final_freq, interval_ms, interval_str

   
    def resample(self, sections: pd.DataFrame, resample_freq, input_freq):
        """
        Resample time series data properly!
        """
        resampled_sections = []

        for section in sections:
            
            # Define target sampling frequency in milliseconds
            resample_period_ms = int(1000 / (resample_freq))

            # Create a regular time grid in milliseconds from timestamp ms
            start_time_ms = section['timestamp_ms'].min()
            end_time_ms = section['timestamp_ms'].max()
            reg_time_index_ms = np.arange(start_time_ms, end_time_ms, resample_period_ms)

            # Interpolate PPG using timestamp_ms
            interpolated_ppg = np.interp(
                reg_time_index_ms, section['timestamp_ms'], section['ppg']
            )

            # Create a new DataFrame for the resampled section
            section_resampled = pd.DataFrame({
                'timestamp_ms': reg_time_index_ms,
                'ppg': interpolated_ppg
            })
            
            resampled_sections.append(section_resampled)
            
        print(f"[PPGPreProcessor] Sensor resampled from {input_freq} Hz to {resample_freq} Hz")

        return resampled_sections 
             

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
