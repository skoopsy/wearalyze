from .compliance_thresholding_corsano import ComplianceThresholdingCorsano
from .compliance_thresholding_polar import ComplianceThresholdingPolar

class ComplianceThresholdingFactory:
    """ 
    Return appropriate thresholding strategy to monitor if the device is worn 
    """

    THRESHOLDING_CLASSES = {
        "corsano287-2b": ComplianceThresholdingCorsano,
        "polar-verity": ComplianceThresholdingPolar
    }

    @staticmethod
    def get_thresholding_strategy(device):
        """ Returns the correct thresholding class for given devices """
        if device not in ComplianceThresholdingFactory.THRESHOLIDING_CLASSES:
            raise ValueError(f"[ComplianceThresholdingFactory] Unsupported device: {device}")
        
        return ComplianceThresholdingFactory.THRESHOLDING_CLASSES[device]() 
