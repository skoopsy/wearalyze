import os
import glob
import pandas as pd
from .loader_factory import DataLoaderFactory

class LoaderOrchestrator:
    def __init__(self, config):
        self.config = config
        ds = config["data_source"]
        self.subjects_dir = ds["subjects_dir"]
        self.multi_subjects = ds["multi_subjects"]
        self.subjects_to_load = ds["subjects_to_load"]
        self.multi_condition_status = ds["multi_condition"]["status"]
        self.conditions = ds["multi_condition"]["conditions"]
        self.device = ds["device"]
        self.sensor_type = ds["sensor_type"]

    def load_all(self):
        """  Load all subjects or a subset specified in the config """

        # Create subject directory list
        if "all" in self.subjects_to_load:
            subject_dirs = [d for d in os.listdir(self.subjects_dir)
                            if os.path.isdir(os.path.join(self.subjects_dir, d))]
        else:
            subject_dirs = self.subjects_to_load
        
        # Create all subject data dict
        data = {}
        for subject in subject_dirs:
            data[subject] = self.load_subject(subject)
        
        return data

    def load_subject(self, subject):
        """ Load a single subjects data """
        subject_path = os.path.join(self.subjects_dir, subject)
        subject_data = {}
        if self.multi_condition_status:
            for condition in self.conditions:
                condition_path = os.path.join(subject_path, condition)
                subject_data[condition] = self.load_condition(condition_path)
        else:
            # If no separate condition structure, treat the subjects folder as one condition
            subject_data["single_condition"] = self.load_condition(subject_path)

        return subject_data

    
    def load_condition(self, condition_path):
        """ Load all sensor data for that condtion """
        # Gather all files in the folder
        files = glob.glob(os.path.join(condition_path, "*"))
        
        condition_data = {}
        
        # Get device specific loader
        loader = DataLoaderFactory.get_loader(self.config)

        # For each sensor type in config - load and standardise the data.
        for sensor in self.sensor_types:
            sensor_data = loader.load_sensor_data(sensor, files)
            if not sensor_data.empty:
                sensor_data = loader.standardise(sensor, sensor_data)
            condition_data[sensor] = sensor_data
        
        return condition_data
                 
