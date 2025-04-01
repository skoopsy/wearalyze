import os
import glob
from typing import List
import pandas as pd

from src.data_model.study_data import StudyData, Subject, SessionData
from .loader_factory import DataLoaderFactory

class LoaderOrchestrator:
    """
    Load all subjects and sessions - build StudyData structure
    """
    def __init__(self, config):
        self.config = config
        ds = config["data_source"]
        self.subjects_dir = ds["subjects_dir"]
        self.subjects_to_load = ds["subjects_to_load"]
        self.sessions = ds["multi_condition"]["conditions"]
        self.device = ds["device"]
        self.sensor_types = ds["sensor_type"]

    def load_study_data(self) -> StudyData:
        study_data = StudyData()

        if "all" in self.subjects_to_load:
            all_dirs = os.listdir(self.subjects_dir)
            subject_dirs = [
                d for d in all_dirs
                if os.path.isdir(os.path.join(self.subjects_dir, d))
            ]

        else:
            subject_dirs = self.subjects_to_load

        for subject_id in subject_dirs:
            subject_path = os.path.join(self.subjects_dir, subject_id)
            subject_obj = Subject(subject_id)

            for session_name in self.sessions:
                session_path = os.path.join(subject_path, session_name)
                if not os.path.isdir(session_path):
                    print(f"[LoaderOrchestrator] Session path '{session_path}' can't be found")
                    continue
                
                session_data = SessionData(session_name, subject_id)

                # Device loader
                loader = DataLoaderFactory.get_loader(self.config)
    
                # Colelct files
                files = glob.glob(os.path.join(session_path, "*"))

                for sensor_type in self.sensor_types:
                    df = loader.load_sensor_data(sensor_type, files)
                    if not df.empty:
                        df = loader.standardise(sensor_type, df)
                    session_data.add_sensor_data(sensor_type, df)

                # add session to subject
                subject_obj.add_session(session_name, session_data)

            # Add subject to study
            study_data.add_subject(subject_obj)

        return study_data
