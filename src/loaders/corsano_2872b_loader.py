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
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')

            data_frames.append(data)

        return pd.concat(data_frames, ignore_index=True)

