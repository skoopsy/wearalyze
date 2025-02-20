import pandas as pd
from .base_loader import BaseLoader

class Corsano2872bLoader(BaseLoader):
    def load_sensor_data(self, file_paths):
        """
        Load data from Corsano 2872b - note the columns may change based
        on options of importing the data from api or portal
        
        :params file_path: List of file paths to load
        :return concatenated pandas dataframe
        """

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

            data_frames.append(data)

        return pd.concat(data_frames, ignore_index=True)

    def standardise(self, data):
        """
        Standardise data from Corsano 2872b
        """
        # Column renaming
        data = self._col_rename_map(data)

        # Convert timestamp to datetime
        #TODO Check datetime against the date column in corsano data
        # Better to have 2 cols - sensor_clock_ms and datetime rather than timestamp
        data['datetime'] = pd.to_datetime(data['timestamp_ms'], unit='ms')
        
        # Make df standardised, drop non numeric columns
        data = data[['datetime','timestamp_ms', 'ppg']]

        return data   

    def _col_rename_map(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Renanme columns to standardise column names for corsano 287-2b
        """

        # Map specifically for Corsano 287-2b from corsano portal
        #TODO change timestamp_ms to sensor_clock_ms for all codebase
        rename_map = {
            'value': 'ppg',
            'timestamp': 'timestamp_ms',    
        }
        
        # If col exist rename them into new mapping
        rename_dict = {col: rename_map[col] for col in df.columns
                       if col in rename_map}

        return df.rename(columns=rename_dict)
