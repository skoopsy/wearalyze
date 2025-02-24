from src.checkpoints.checkpoint_manager import CheckpointManager
from src.checkpoints.checkpoint_decorator import with_checkpoint
from src.preprocessors.ppg_preprocess import PPGPreProcessor
from src.processors.beat_detectors.beat_detection import HeartBeatDetector
from src.processors.sqi.beat_organiser import BeatOrganiser
from src.processors.biomarkers.basic_biomarkers import BasicBiomarkers
from src.processors.biomarkers.pulse_wave_features2 import PulseWaveFeatures
from src.processors.sqi.factory import SQIFactory
from src.visuals.plots import Plots

import os

class PPGPipeline:
    def __init__(self, sensor, config):
        self.sensor = sensor
        self.config = config
        self.CONF_preprocess = config["ppg_preprocessing"]
        self.checkpoint = CheckpointManager(config=config['checkpoint']['pipeline_ppg'])

    def run(self):
        
        sections = self._preprocess()
        grouped_beats, all_beats = self._process_beats(sections)
        data = self._basic_biomarkers(grouped_beats)
        sqi_results = self._basic_sqi(data)
        #Plots.all_deteted_toughs_and_peaks(data, 'filtered_value')
        data, beat_features = self._pulse_wave_features(data)
        for i in range(1000,1100, 1):
            Plots.plot_beat_with_features_deriv(data, beat_features, i)
        breakpoint()
             
        return data, beat_features

    def _preprocess(self):
        print("[PPGPipeline] Preprocessing PPG data.")
        preprocessor = PPGPreProcessor(self.sensor.data, self.config)
        sections = preprocessor.create_compliance_sections()
        sample_freq, _, _ = preprocessor.compute_sample_freq(sections)
        resampled_sections = preprocessor.resample(sections=sections, 
                                                   resample_freq=self.CONF_preprocess.get("resample_freq"),
                                                   input_freq=sample_freq)
        preprocessor.filter_cheby2(resampled_sections)
        return resampled_sections
    
    @with_checkpoint(checkpoint_id=2, stage_name="process_beats")
    def _process_beats(self, sections):
        print("[PPGPipeline] Processing beats.")
        heartbeat_detector = HeartBeatDetector(self.config)
        combined_sections, all_beats = heartbeat_detector.process_sections(sections)
        organiser = BeatOrganiser(group_size=self.config["ppg_processing"]["sqi_group_size"])
        grouped_beats = organiser.group_n_beats_inplace(combined_sections)
        
        return grouped_beats, all_beats 
        
    def _basic_biomarkers(self, data):
        print("[PPGPipeline] Computing basic biomarkers.")
        biomarkers = BasicBiomarkers(data)
        data = biomarkers.compute_ibi()
        data = biomarkers.compute_bpm_from_ibi_group()
        biomarkers.compute_group_ibi_stats()
        
        return data

    def _basic_sqi(self, data):
        print("[PPGPipeline] Computing basic SQI.")
        sqi = SQIFactory.create_sqi(
            sqi_type=self.config["ppg_processing"]["sqi_type"],
            sqi_composite_details=self.config["ppg_processing"]["sqi_composite_details"]
        )
        sqi_results = sqi.compute(data)
        
        return sqi_results

    def _pulse_wave_features(self, data):
        print("[PPGPipeline] Computing pulse wave features.")
        pwf = PulseWaveFeatures(data)
        data, beat_features = pwf.compute()
        
        return data, beat_features
        
