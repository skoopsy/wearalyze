import os
import pandas as pd
import re
from src.checkpoints.checkpoint_manager import CheckpointManager

class MultiSubjectLoader:
    def __init__(self, config):
        self.config = config

        ms_config = config['multi_subect_settings']
        self.data_dir = ms_config['data_dir']
        self.conditions = ms_config['sensor_types']
        
        # Remove checkpoint logic from here.
        self.load_from_checkpoint
