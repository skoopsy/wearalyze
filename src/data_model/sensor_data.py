import pandas as pd

class SensorData:
    """ Encapsulates sensor data for specified sensor """
    def __init__(self, sensor_type: str, data: pd.DataFrame):
        self.sensor_type = sensor_type
        self.data = data
    
    def get_data(self) -> pd.DataFrame:
        """
        Return the sensor data DataFrame
        """
        return self.data

    def __repr__(self) -> str:
        return f"SensorData(sensor_type={self.sensor_type}, rows={len(self.data)})"
