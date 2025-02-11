from .compliance_check_corsano_2872b import ComplianceCheckCorsano2872b
from .compliance_check_polar_verity import ComplianceCheckPolarVerity

class ComplianceCheckFactory:
    """ 
    Return appropriate thresholding strategy to monitor if the device is worn 
    """

    DEVICE_CLASSES = {
        "corsano287-2b": ComplianceCheckCorsano2872b,
        "polar-verity": ComplianceCheckPolarVerity
    }

    @staticmethod
    def get_check_method(device):
        """ Returns the correct device-specific check class """

        if device not in ComplianceCheckFactory.DEVICE_CLASSES:
            raise ValueError(f"[ComplianceCheckFactory] Unsupported device: {device}")
        
        return ComplianceCheckFactory.DEVICE_CLASSES[device]() 
