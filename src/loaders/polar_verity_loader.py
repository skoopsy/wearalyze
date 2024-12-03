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
            required_columns = [
                "Phone timestamp", "sensor timestamp [ns]",
                "channel 0", "channel 1", "channel 2", "ambient"
            ]
    
            for file_path in file_paths:
                data = pd.read_csv(file_path, delimiter=';')
                
                # Check cols
                if not set(required_columns).issubset(data.columns):
                    raise ValueError(f"File {file_path} is missing required columns. Expected {required_columns}")

                # Change timestamp from ns to ms for standardisation
                data['timestamp'] = data['sensor timestamp [ns]']/1000000	
                data_frames.append(data)

            return pd.concat(data_frames, ignore_index=True)

