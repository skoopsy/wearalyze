from src.processors.sqi.base import SQIBase

import pandas as pd

class SQIIBIRatioGroup(SQIBase):
    def compute(self, data):
        """
        Check if max IBI / Min IBI of a small group is plausible roughly 10seconds
        """
    
        ratio_threshold_max = 1.1
        
        # Handle None values for vectorisation math
        data['ibi_max_group'] = pd.to_numeric(data['ibi_max_group'], errors='coerce')
        data['ibi_min_group'] = pd.to_numeric(data['ibi_max_group'], errors='coerce')

        # Compute ratio
        ratio = data['ibi_max_group'] / data['ibi_min_group']
       
        # Check ratio is below max threshold
        data['sqi_ibi_ratio_group'] = (ratio < ratio_threshold_max) & ratio.notnull()
