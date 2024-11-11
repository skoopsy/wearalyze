from .polar_verity_loader import PolarVerityLoader
from .corsano_2872b_loader import Corsano2872bLoader

class DataLoaderFactory:
	@staticmethod
	def get_loader(device, sensor_type):
		if device == 'polar-verity' and sensor_type == 'PPG':
			return PolarVerityLoader()
		elif device == 'corsano-2872b' and sensor_type == 'PPG':
			return Corsano2872bLoader()
		else: 
			raise ValueError(f"Unsupported device {device} or sensor type {sensor_type}")	
