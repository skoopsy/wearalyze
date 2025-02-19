from src.checkpoints.checkpoint_manager import CheckpointManager
from src.preprocessors.ppg_preprocess import PPGPreProcessor
from src.processors.beat_detectors.beat_detection import HeartBeatDetector
from src.processors.sqi.beat_organiser import BeatOrganiser
from src.processors.biomarkers.basic_biomarkers import BasicBiomarkers
from src.processors.biomarkers.pulse_wave_features import PulseWaveFeatures
from src.processors.sqi.factory import SQIFactory
from src.visuals.plots import Plots

import os

class PPGPipeline:
    def __init__(self, sensor, config):
        self.sensor = sensor
        self.config = config
        self.checkpoint = CheckpointManager(config=config)

    def run(self):
        print("[PPGPipeline] Preprocessing PPG data")
        
        # Checkpoint load
        if self.checkpoint.get_load_status() and self.checkpoint.get_load_id == 2:
            print("[PPGPineline] Loading from checkpoint 2")
            return self.checkpoint.load()
       
        # Start pipeline 
        preprocessor = PPGPreProcessor(self.sensor.data, self.config)
        #TODO section thresholding is for corsano only, polar? Have tweaked config
        sections = preprocessor.create_compliance_sections()
         
        resample_freq, _, _ = preprocessor.compute_sample_freq(sections)
        resampled_sections = preprocessor.resample(sections, resample_freq)

        preprocessor.filter_cheby2(resampled_sections)
        
        heartbeat_detector = HeartBeatDetector(self.config)
        combined_sections, all_beats = heartbeat_detector.process_sections(resampled_sections)

        organiser = BeatOrganiser(group_size=self.config["ppg_processing"]["sqi_group_size"])
        data = organiser.group_n_beats_inplace(combined_sections)
    
        biomarkers = BasicBiomarkers(data)
        data = biomarkers.compute_ibi()
        data = biomarkers.compute_bpm_from_ibi_group()
        biomarkers.compute_group_ibi_stats()

        # Checkpoint
        if self.checkpoint.get_save_status() and self.checkpoint.get_save_id() == 3:
            chkpnt_path = self.checkpoint.get_save_path()
            print(f"[PPGPipeline] Saving checkpoint 3: {chkpnt_path}")
            self.checkpoint.save(data)

        if self.checkpoint.get_load_status() and self.checkpoint.get_load_id() == 3:
            chkpnt_path = self.checkpoint.get_load_path()
            print(f"[PPGPineline] Loading checkpoint 3:{chkpnt_path}")

        # Continue
        sqi = SQIFactory.create_sqi(
            sqi_type=self.config["ppg_processing"]["sqi_type"],
            sqi_composite_details=self.config["ppg_processing"]["sqi_composite_details"]
        )
        sqi_results = sqi.compute(data)

        pwf = PulseWaveFeatures(data)
        data, beat_features = pwf.compute()
        
        breakpoint()
        return data, beat_features                 
