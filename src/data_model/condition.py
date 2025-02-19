from .sensor_data import SensorData

from typing import Dict

class Condition:
    """
    Represents a specific condition for a subject, containing multiple
    sensor datasets
    """
    
    def __init__(self, name: str):
        self.name = name
        self.sensors: Dict[str, SensorData] = {}
        
    def add_sensor_data(self, sensor_data: SensorData) -> None:
        """
        Add sensor data to this condition

        Args:
            sensor_data (SensorData): Sensor data obj to add
        """
    
        self.sensors[sensor_data.sensor_type] = sensor_data

    def get_sensor_data(self, sensor_type: str) -> SensorData:
        """
        Retrive sensor data for sensor type

        Args:
            sensor_type (str): Type of sensor to retrive

        Returns:
            SensorData: The sensor data for the requested sensor type
        """
        return self.sensors.get(sensor_type)

    def __repr__(self) -> str:
        return f"Condition(name={self.name}, sensors={list(self.sensors.keys())})"


