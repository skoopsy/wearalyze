from src.processors.sqi.bpm_plausible import SQIBpmPlausible

class SQIFactory:
    @staticmethod
    def create_sqi(sqi_type: str):
        if sqi_type == "bpm_plausible":
            return SQIBpmPlausible()
        else:
            raise ValueError(f"Unknown SQI: {sqi_type}")
