from src.processors.beat_detector_msptd import beat_detect_msptd
from src.processors.beat_detector_ampd import peak_detect_ampd

class BeatDetectorFactory:
    @staticmethod
    def get_beat_detector(detector_name):
        detectors = {
            'ampd': peak_detect_ampd,
            'msptd': beat_detect_msptd,
        }
        
        if detector_name not in detectors:
            raise ValueError(f"Invalid beat detector: {detector_name}")
        return detectors[detector_name]
