from src.processors.sqi.composite_sqi import CompositeSQI
from src.processors.sqi.bpm_plausible import SQIBpmPlausible
from src.processors.sqi.ibi_max import SQIIBIMax

class SQIFactory:
    @staticmethod
    def create_sqi(sqi_type: str, sqi_composite_details):
        """
        Create a Signal Quality Index (SQI) instance based on the type
        
        args:
            sqi_type (str): The type of SQI to create 
            composite_details (dict, optional): Details for creating a composite SQI.
        
        returns:
            SQI: An instance of the requested SQI type
        """
        if sqi_type == "bpm_plausible":
            return SQIBpmPlausible()

        if sqi_type == "ibi_max":
            return SQIIBIMax()

        elif sqi_type == "composite":
            if not sqi_composite_details or "sqi_types" not in sqi_composite_details:
                raise ValueError(f"Composite SQI requires 'sqi_types' in sqi_composite_details.")

            sqi_list = [
                SQIFactory.create_sqi(sqi_type=sqi_name, sqi_composite_details=sqi_composite_details)
                for sqi_name in sqi_composite_details["sqi_types"]
            ]
            combine_strategy = sqi_composite_details.get("combine_strategy")
            
            return CompositeSQI(sqi_list, combine_strategy=combine_strategy)

        else:
            raise ValueError(f"Unknown SQI: {sqi_type}")
