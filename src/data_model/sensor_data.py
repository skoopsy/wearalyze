import pandas as pd

class SensorData:
    """ Encapsulates sensor data for specified sensor """
    def __init__(self, sensor_type: str, data: pd.DataFrame, subject=None, conditon=None):
        self.sensor_type = sensor_type
        self.data = data
        self.subject = subject
        self.condition = condition
    
    def get_data(self) -> pd.DataFrame:
        """
        Return the sensor data DataFrame
        """
        return self.data

    def get_subject(self):
        return self.subject

    def get_condition():
        return self.condition

    def __repr__(self) -> str:
        return f"SensorData(sensor_type={self.sensor_type}, rows={len(self.data)})"
