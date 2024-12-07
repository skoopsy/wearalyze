from src.processors.sqi.composite_sqi import CompositeSQI
from src.processors.sqi.bpm_plausible import SQIBpmPlausible

class SQIFactory:
    @staticmethod
    def create_sqi(sqi_type: str, composite_details=None):
        """
        Create a Signal Quality Index (SQI) instance based on the type
        
        args:
            sqi_type (str): The type of SQI to create 
            composite_details (dict): Details for creating a composite SQI.
        
        returns:
            SQI: An instance of the requested SQI type
        """
        if sqi_type == "bpm_plausible":
            return SQIBpmPlausible()

        elif sqi_type == "composite":
            if not composite_details or "sqi_types" not in composite_details:
                raise ValueError(f"Composite SQI requires 'sqi_types' in details.")
            sqi_list = [
                SQIFactory.create_sqi(sqi_type=sqi_name)
                for sqi_name in composite_details["sqi_types"]
            ]
            combine_strategy = composite_details.get("combine_strategy")
            
            return CompositeSQI(sqi_list, combine_strategy=combine_strategy)

        else:
            raise ValueError(f"Unknown SQI: {sqi_type}")
