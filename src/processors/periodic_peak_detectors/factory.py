from src.processors.periodic_peak_detectors.ampd import AMPDDetector
from src.processors.periodic_peak_detectors.msptd import MSPTDDetector

class PeakDetectorFactory:
    @staticmethod
    def create(detector_name: str):
        detectors = {
            "ampd": AMPDDetector(),
            "msptd": MSPTDDetector(),
        }
        if detector_name not in detectors:
            raise ValueError(f"Unkniwn detector: {detector_name}")
        return detectors[detector_name]
