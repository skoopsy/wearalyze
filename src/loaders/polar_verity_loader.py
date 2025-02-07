import pandas as pd
from .base_loader import BaseLoader

class PolarVerityLoader(BaseLoader):
    def load_data(self, file_paths):
        """
        Load data from a list of file paths
    
        :params file_path: List of file paths 
        :return: Concatenated pandas Datafram
        """

        data_frames = []

        #TODO change to be dynamically set by sensors based in configuration
        required_columns = ["Phone timestamp", "sensor timestamp [ns]",
                            "channel 0", "channel 1", "channel 2", "ambient"
                            ] 
    
        for file_path in file_paths:
            data = pd.read_csv(file_path, delimiter=';')
        
            # Check cols
            if not set(required_columns).issubset(data.columns):
                raise ValueError(f"File {file_path} is missing required columns. Expected {required_columns}")

            data_frames.append(data)

        return pd.concat(data_frames, ignore_index=True)

    def standardise(self, data):
        """
        Standardise Polar Verity Sense data
        """

        # Change timestamp from ns to ms for standardisation
        data['timestamp_ms'] = data['sensor timestamp [ns]']/1000000	

        # Column remapping
        data = self._col_name_remap(data)
        
        #TODO This method may need to be stated in config, probably better methods, maybe even kalman. 
        # Avg 3 ppg channels
        data['ppg'] = data[["ppg_ch0","ppg_ch1", "ppg_ch2"]].mean(axis=1)
                
        #TODO Could remove unused columns here to keep memory lower, for later
        # data = data[['timestamp_ms','ppg']]
 
        return data
    
    def _col_name_remap(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename columns to standardised column names for polar verity sense
        """
        
        # Map specifically for Polar Verity Sense - Polar Logger App (Android)    
        rename_map = {
            'Phone timestamp': 'phone_datetime',
            'sensor timestamp [ns]': 'sensor_clock_ns',
            'channel 0': 'ppg_ch0',
            'channel 1': 'ppg_ch1',
            'channel 2': 'ppg_ch2',
            'ambient': 'ppg_amb',
            'X [mg]': 'acc_x_mg',
            'Y [mg]': 'acc_y_mg',
            'Z [mg]': 'acc_z_mg',
            'X [dps]': 'gyr_x_dps',
            'Y [dps]': 'gyr_y_dps',
            'Z [dps]': 'gyr_z_dps',
            'HR [bpm]': 'hr_bpm',
        }

        # If cols exist rename them into a new mapping
        rename_dict = {col: rename_map[col] for col in df.columns 
                       if col in rename_map}

        return df.rename(columns=rename_dict)        
