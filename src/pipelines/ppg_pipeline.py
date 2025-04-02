from src.checkpoints.checkpoint_manager import CheckpointManager
from src.checkpoints.checkpoint_decorator import with_checkpoint
from src.preprocessors.ppg_preprocess import PPGPreProcessor
from src.processors.beat_detectors.beat_detection import HeartBeatDetector
from src.processors.sqi.beat_organiser import BeatOrganiser
from src.processors.biomarkers.basic_biomarkers import BasicBiomarkers
from src.processors.biomarkers.pulse_wave_features2 import PulseWaveFeatures
from src.processors.sqi.factory import SQIFactory
from src.visuals.plots import Plots # for debugging

import pandas as pd
#import os

class PPGPipeline:
    def __init__(self, config):
        self.config = config
        self.CONF_preprocess = config["ppg_preprocessing"]
        self.checkpoint = CheckpointManager(config['checkpoint']['pipeline_ppg'])

    def run(self, raw_ppg_df:pd.DataFrame ):
        """ Main entry for pipeline """
        if raw_ppg_df.empty:
            print("[PPGPipeline] Empty df")
            return raw_ppg_df, None
        
        sections = self._preprocess(raw_ppg_df)
        grouped_beats, all_beats = self._process_beats(sections)
        data = self._basic_biomarkers(grouped_beats)
        sqi_results = self._basic_sqi(data)
        data, beat_features = self._pulse_wave_features(data)
        #breakpoint() 
        #Plots.all_deteted_toughs_and_peaks(data, 'filtered_value')
        #breakpoint()
        #for i in range(1000,1100, 1):
        #    Plots.plot_beat_with_features_deriv(data, beat_features, i)
        #breakpoint()
             
        return data, beat_features

    def _preprocess(self, raw_ppg_df: pd.DataFrame):
        """
        Preprocessing of ppg data
        - Check compliance
        - Sample freq estimation
        - Resampling
        - Basic filtering (bandpass)
        """
        print("[PPGPipeline] Preprocessing PPG data.")
        preprocessor = PPGPreProcessor(raw_ppg_df, self.config)
        sections = preprocessor.create_compliance_sections()
        sample_freq, _, _ = preprocessor.compute_sample_freq(sections)
        resampled_sections = preprocessor.resample(sections=sections, 
                                                   resample_freq=self.CONF_preprocess.get("resample_freq"),
                                                   input_freq=sample_freq)
        preprocessor.filter_cheby2(resampled_sections, self.CONF_preprocess.get("resample_freq"))

        return resampled_sections
    
    @with_checkpoint(checkpoint_id=2, stage_name="process_beats")
    def _process_beats(self, sections):
        """
        Detects and annotates pulses from preprocessed sections
        Group beats (BeatOrganiser) in essentially epochs
        """
        print("[PPGPipeline] Processing beats.")
        heartbeat_detector = HeartBeatDetector(self.config)
        combined_sections, all_beats = heartbeat_detector.process_sections(sections)
        organiser = BeatOrganiser(group_size=self.config["ppg_processing"]["sqi_group_size"])
        grouped_beats = organiser.group_n_beats_inplace(combined_sections)
        
        return grouped_beats, all_beats 
        
    def _basic_biomarkers(self, data):
        """
        Compute biomarkers like IBI and BPM, things that do not require
        specific pulse wave features from within a single pulse wave, 
        maybe these should be called low resolution biomarkers. 
        """
        print("[PPGPipeline] Computing basic (low-resolution) biomarkers.")
        biomarkers = BasicBiomarkers(data)
        data = biomarkers.compute_ibi()
        data = biomarkers.compute_bpm_from_ibi_group()
        biomarkers.compute_group_ibi_stats()
        
        return data

    def _basic_sqi(self, data):
        """
        Compute signal quality indicies (SQIs) for low-resolution biomarkers
        """
        print("[PPGPipeline] Computing basic SQI.")
        sqi = SQIFactory.create_sqi(
            sqi_type=self.config["ppg_processing"]["sqi_type"],
            sqi_composite_details=self.config["ppg_processing"]["sqi_composite_details"]
        )
        sqi_results = sqi.compute(data)
        
        return sqi_results

    def _pulse_wave_features(self, data):
        """
        Compute high-resolution biomarkers based on intra-pulse features
        """
        print("[PPGPipeline] Computing pulse wave features.")
        pwf = PulseWaveFeatures(data)
        data, beat_features = pwf.compute()
        
        return data, beat_features
        
