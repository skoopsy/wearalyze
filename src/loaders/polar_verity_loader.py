import os
import re
import pandas as pd

from .base_loader import BaseLoader

class PolarVerityLoader(BaseLoader):

    def __init__(self, config):
        self.config = config

        # Polar Verity Sense file regex patterns - Polar Sensor Logger (Android)
        self.sensor_patterns = {
            "hr": r".*_HR\.txt",
            "ppg": r".*_PPG\.txt",
            "acc": r".*_ACC\.txt",
            "gyro": r".*_GYRO\.txt"
        }

        # Check correct columns are in the data file
        self.required_columns = {
            "hr": ["Phone timestamp", "sensor timestamp [ns]", "HR [bpm]"],
            "ppg": ["Phone timestamp", "sensor timestamp [ns]", "channel 0", "channel 1", "channel 2", "ambient"],
            "acc": ["Phone timestamp", "sensor timestamp [ns]", "X [mg]", "Y [mg]", "Z [mg]"],
            "gyro": ["Phone timestamp", "sensor timestamp [ns]", "X [dps]", "Y [dps]", "Z [dps]"]
        }


    def load_sensor_data(self, sensor, files):
        """
        For a sensor type and list of file paths, filter files using device
        specific regex and load the data into a DataFrame - Combining all files
        with same sensor type
        """
        
        # Get sensor file names
        pattern =self.sensor_patterns.get(sensor)
        if pattern is None:
            raise ValueError(f"Sensor type not supported / incorrect: {sensor}")

        sensor_files = [f for f in files if re.search(pattern, os.path.basename(f))]
        if not sensor_files:
            raise ValueError(f"PolarVerityLoader.py: No files found for sensor: {sensor}")
            return pd.DataFrame() # Empty df

        data = []
        req_cols = self.required_columns.get(sensor)

        for file_path in sensor_files:
            file_data = pd.read_csv(file_path, delimiter=";", usecols=req_cols)
            if not set(req_cols).issubset(file_data.columns):
                raise ValueError(f"File {file_path} is missing required columns for sensor: {sensor}. Expected {req_cols}")
            data.append(file_data)
        
        return pd.concat(data, ignore_index=True)
    
    def standardise(self, sensor_type, data):
        """
        Standardise Polar Verity Sense data
        """
        
        if "sensor timestamp [ns]" in data.columns:
            # Change timestamp from ns to ms for standardisation
            data['timestamp_ms'] = data['sensor timestamp [ns]']/1000000	
        # Column remapping
        data = self._col_name_remap(data)
        
        #TODO This method may need to be stated in config, probably better methods, maybe even kalman. 
        # Avg 3 ppg channels
        if sensor_type == "ppg":
            data['ppg'] = data[["ppg_ch0","ppg_ch1", "ppg_ch2"]].mean(axis=1)
                
        #TODO Could remove unused columns here to keep memory lower, for later
 
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
