import pandas as pd
from .base_loader import BaseLoader

class PolarVerityLoader(BaseLoader):
        def load_data(self, file_path):
            data_frames = []
            for file_path in file_paths:
                data = pd.read_csv(file_path)

                # Change timestamp from ns to ms for standardisation
                data['timestamp'] = data['sensor timestamp [ns]']/1000000	
                data_frames.append(data)

            return pd.concat(data_frames, ignore_index=True)

