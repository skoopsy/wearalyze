from src.processors.sqi.base import SQIBase

class SQIMaxIBI(SQIBase):
    def compute(self, data):
        """
        Check every IBI and filter out IBIs greater than threshold
        """
        min_bpm = 30 # Could dynamically link this to other sqi or config
        max_ibi = 60000 / min_bpm # in miliseconds
        
        # Check
        data['sqi_max_ibi'] = data.apply(
            lambda row: self.max_ibi_check(row, ibi_ms, max_ibi), axis=1
        )
        
        return data

    def max_ibi_check(self, row, col, max_ibi):
        return row[col] < max_ibi
