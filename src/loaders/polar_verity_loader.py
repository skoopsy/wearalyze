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
                
        # Avg 3 ppg channels
        data['ppg'] = data[["channel 0","channel 1", "channel 2"]].mean(axis=1)
                
        # Could remove unused columsn here to keep memory lower, for later
        # data = data[['timestamp_ms','ppg']]
 
        return data
