from src.processors.sqi.base import SQIBase
import pandas as pd

class SQIIBIMax(SQIBase):
    def compute(self, data):
        """
        Check every IBI and filter out IBIs greater than threshold
        """
        min_bpm = 30 # Could dynamically link this to other sqi or config
        max_ibi = 60000 / min_bpm # in miliseconds
        
        data['ibi_max_group'] = pd.to_numeric(data['ibi_max_group'], errors='coerce')
        
        data['sqi_ibi_max'] = data['ibi_max_group'] < max_ibi
        
        return data
