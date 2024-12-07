from src.processors.sqi.base import SQIBase

class SQIBpmPlausible(SQIBase):
    def compute(self, segment):
        """ Check for plausible BPM """
        max_bpm = 180
        min_bpm = 30
        
        # Find peak with corresponding time
        # For each peak from IBI
        # Average IBI over all beats
        # Avg IBI convert to BPM or vise-versa
        
        #Place holder
        bpm = 100
        
        if bpm < max_bpm and bpm > min_bpm:
            result = True
        else:
            result = False

        return result
