from .polar_verity_loader import PolarVerityLoader
from .corsano_2872b_loader import Corsano2872bLoader

class DataLoaderFactory:
    @staticmethod
    def get_loader(config): 
        device = config["data_source"]["device"]
        if device == 'polar-verity':
            return PolarVerityLoader(config=config)
        elif device == 'corsano-2872b': 
            return Corsano2872bLoader(config=config)
        else:
            raise ValueError(f"Unsupported device {device}")	
