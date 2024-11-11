import pandas as pd
from .base_loader import BaseLoader

class Corsano2872bLoader(BaseLoader):
	def load_data(self, file_paths):
		data_frames = []
		for file_path in file_paths:
			data = pd.read_csv(file_path)
			
			data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')

			data_frames.append(data)

		return pd.concat(data_frames, ignore_index=True)

