import pandas as pd
from .base_loader import BaseLoader

class Corsano2872bLoader(BaseLoader):
    def load_data(self, file_paths):
        data_frames = []
        required_columns = [
        "timestamp", "date", "metric_id", "chunk_index",
        "quality", "body_pose", "led_pd_pos", "offset",
        "exp", "led", "gain", "value"
        ]

        for file_path in file_paths:
            data = pd.read_csv(file_path)

            # Validate columns
            if not set(required_columns).issubset(data.columns):
                raise ValueError(f"File {file_path} is missing required columns. Expected {required_columns}")

            # Convert timestamp to datetime
            data['timestamp_ms'] = pd.to_datetime(data['timestamp'], unit='ms')
            
            # Rename the ppg channel
            data['ppg'] = data['value']

            # Maybe remove unused data here if mem requirements get too big
            # data = data [['timestamp_ms, 'ppg']]

            data_frames.append(data)

        return pd.concat(data_frames, ignore_index=True)

