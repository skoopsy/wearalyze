import pandas as pd
from typing import Dict, Any


class EpochData:
    """
    Represents a epoch of data which is defined by user such as 60s or 10 
    heart beats etc. The segment of data that multi beat features and cross-
    sensor features are calculated and added to.
    """

    def __init__(self, epoch_id: str, start_time: float, end_time: float):
        self.epoch_id = epoch_id
        self.start_time = start_time
        self.end_time = end_time

        # Sensor features e.g {'ppg': {'avg hr':70, ...}, 'acc': {...}}
        self.sensor_features: Dict[str, Dict[str, Any]] = {}

        # Cross sensor features e.g. {'motion artefact': True, ...}
        self.cross_sensor_features: Dict[str, Any] = {}

    def add_sensor_features(self, sensor_type: str, features: Dict[str, Any]):
        if sensor_type not in self.sensor_features:
            self.sensor_features[sensor_type] = {}
        self.sensor_features[sensor_type].update(features)

    def __repr__(self):
        return (f"EpochData(id={self.epoch_id}, "
                f"time=[{self.start_time}, {self.end_time}], "
                f"sensors={list(self.sensor_features.keys())}, "
                f"cross={list(self.cross_sensor_features.keys())} "
        )


class SessionData:
    """
    One session for a subject. Holds multiple sensor data frames, could be
    raw or processed data, and epochs.
    """

    def __init__(self, session_name: str, subject_id: str):
        self.session_name = session_name
        self.subject_id = subject_id

        # Sensor data
        self.sensors: Dict[str, pd.DataFrame] = {}

        # pipeline outputs
        self.processed: Dict[str, pd.DataFrame] = {}

        # Epochs - segmented analysis results
        self.epochs: Dict[str, EpochData] = {}

    def add_sensor_data(self, sensor_type: str, data: pd.DataFrame):
        self.sensors[sensor_type] = data

    def get_sensor_data(self, sensor_type: str) -> pd.DataFrame:
        return self.sensors.get(sensor_type, pd.DataFrame())

    def add_epoch(self, epoch: EpochData):
        self.epochs[epoch.epoch_id] = epoch

    def get_epoch(self, epoch_id: str) -> EpochData:
        return self.epochs.get(epoch_id, None)

    def __repr__(self):
        return (f"SessionData(subject={self.subject_id}, "
                f"session={self.session_name}, "
                f"sensors={list(self.sensors.keys())}, "
                f"epochs={list(self.epochs.keys())}"
        )

class Subject:
    """
    A subject with one or more sessions of data.
        - A session could be a change in experimental variable such as 
          environment
    """

    def __init__(self, subject_id: str):
        self.subject_id = subject_id
        self.sessions: Dict[str, SessnionData] = {}

    def add_session(self, session_name: str, session_data: SessionData):
        self.sessions[session_name] = session_data

    def get_session(self, session_name: str) -> SessionData:        
        return self.sessions.get(session_name, None)

    def __repr__(self):
        return f"Subject(id={self.subject_id}, sessions={list(self.sessions.keys())})"

 
class StudyData:
    """
    Main container for all data for a study
    """
    
    def __init__(self):
        self.subjects: Dict[str, Subject] = {}

    def add_subject(self, subject: Subject):
        self.subjects[subject.subject_id] = subject

    def get_subject(self, subject_id: str) -> Subject:
        return self.subjects.get(subject_id, None)

    def __repr__(self):
        return f"StudyData(subjects={list(self.subjects.keys())})"

   
