from src.loaders.config_loader import get_config
from src.loaders.loader_factory import DataLoaderFactory

from src.preprocessors.ppg_preprocess import PPGPreProcessor

from src.processors.beat_detectors.beat_detection import HeartBeatDetector
from src.processors.sqi.beat_organiser import BeatOrganiser
from src.processors.biomarkers.basic_biomarkers import BasicBiomarkers
from src.processors.biomarkers.pulse_wave_features import PulseWaveFeatures
from src.processors.sqi.factory import SQIFactory

from src.visuals.plots import Plots

import matplotlib.pyplot as plt
import pandas as pd
import os
import pyarrow.feather as feather # Hopefully can remove in prod

# General todos
#TODO refactor methods to have a from_config() method to optionally take args from config directly
#TODO add tests for all the extra classes fromt the past week! 12/12/2024

def main():
    # Parse cmd line args and load config
    config = get_config()

    # Extract config params
    #TODO Make this a struct and abstact unloading away
    #TODO Create from_config() functions in each class to feed config in optionally
    verbosity = config['outputs']['print_verbosity']
    debug_plots = config['outputs']['debug_plots']
    file_paths = config['data_source']['file_paths']
    device = config['data_source']['device']
    sensor_type = config['data_source']['sensor_type']
    threshold = config['ppg_preprocessing']['threshold']
    beat_detector_name = config["ppg_processing"]["beat_detector"]
    sqi_group_size = config["ppg_processing"]["sqi_group_size"]
    sqi_type = config["ppg_processing"]["sqi_type"]
    sqi_composite_details = config["ppg_processing"]["sqi_composite_details"]
    load_from_checkpoint = config["checkpoints"]["load_from_checkpoint"]
    checkpoint_save = config["checkpoints"]["checkpoint_save"]
    checkpoint_dir = config["checkpoints"]["directory"]
    checkpoint_id = config["checkpoints"]["checkpoint_id"]
    checkpoint_data_id = config["checkpoints"]["data_id"]

    checkpoint_file = f"{checkpoint_dir}/{checkpoint_id}_{checkpoint_data_id}.feather"
    
    if not load_from_checkpoint:

        # Load data
        loader = DataLoaderFactory.get_loader(device, sensor_type)
        data = loader.load_data(file_paths)
        data = loader.standardise(data)
        breakpoint()

        if verbosity >= 1: 
            print("Finished loading data")

        # Preprocess PPG data
        preprocessor = PPGPreProcessor(data, config)
        #TODO thresholding might not work for polar, only corsano:
        sections = preprocessor.create_thresholded_sections() # Get sections where device was worn

        if verbosity > 1:
            for i, section in enumerate(sections):
                print(f"Section {i+1} data points: {len(section)}") 

        
        # Apply resmapling to regularise intervals of measured data
        # keeps sample freq the same
        resample_freq, _, _ = preprocessor.compute_sample_freq(sections)
        resampled_sections = preprocessor.resample(sections, resample_freq)

        #Plots.ppg_series(resampled_sections[3].ppg)
        Plots.ppg_series_compare_datetime(sections[0].reset_index(), resampled_sections[0]) 
 
        # Apply bandpass filter - Creates new column 'filtered_value' in df
        preprocessor.filter_cheby2(resampled_sections)
        
        # Debugging prints
        if verbosity >= 1:
            print("Finished bandpass filtering  sections")
        
        # Plot entire compliance sections
        #Plots.plot_ppg_sections_vs_time(filtered_sections)
    
        # Detect and annotate heart beats
        heartbeat_detector = HeartBeatDetector(config)
        combined_sections, all_beats = heartbeat_detector.process_sections(resampled_sections)
       
        if verbosity >= 1:
            print("Heart Beat Detection Complete")
        
        # Create checkpoint - mostly for development
        # Save df as arrow file
        if checkpoint_save:
            combined_sections.reset_index(drop=True).to_feather(checkpoint_file)
            print(f"Checkpoint created: combined_sections saved to {checkpoint_file}")
         
    if load_from_checkpoint and checkpoint_id == 1:
        combined_sections = pd.read_feather(checkpoint_file)
    if debug_plots: 
        Plots.all_detected_troughs_and_peaks(combined_sections, 'filtered_value')

    # Organise beats into n-beat segments
    organiser = BeatOrganiser(group_size=sqi_group_size)
    data = organiser.group_n_beats_inplace(combined_sections)
    
    # Calc some biomarker
    biomarkers = BasicBiomarkers(data)
    data = biomarkers.compute_ibi()
    data = biomarkers.compute_bpm_from_ibi_group()
    biomarkers.compute_group_ibi_stats()
    
    if debug_plots:
        # Plot HR distribution
        beats = len(data[data.is_beat_peak == True])
        plot_txt = f"Beats = {str(beats)}"
        Plots.group_hr_distribution(data, bins=50, title_append = plot_txt)    

    # Compute SQI   
    sqi = SQIFactory.create_sqi(sqi_type=sqi_type, sqi_composite_details=sqi_composite_details)
    sqi_results = sqi.compute(data) # Setting for clarity, be careful data is from sqi too now as inplace
    if debug_plots:
        # Plot some basic SQI results
        sqi_bpms = data[data.sqi_bpm_plausible == True] 
        sqi_bpms_peaks = sqi_bpms[sqi_bpms.is_beat_peak == True]
        rows = len(sqi_bpms_peaks)
        plot_txt = f"SQI: Avg BPM, Totals Heart Beats: str({rows})"
        Plots.group_hr_distribution(sqi_bpms_peaks, bins=50, title_append=plot_txt)
        
        sqi_ibis = sqi_bpms[sqi_bpms.sqi_ibi_max == True]
        rows = len(sqi_ibis[sqi_ibis.is_beat_peak == True])
        plot_txt = f"SQI: IBI Max, Totals Heart Beats: str({rows})"
        Plots.group_hr_distribution(sqi_ibis, bins=50, title_append=plot_txt)

        sqi_ibi_ratio = sqi_ibis[sqi_ibis.sqi_ibi_ratio_group == True]
        rows = len(sqi_ibi_ratio[sqi_ibi_ratio.is_beat_peak == True ])
        plot_txt = f"SQI: IBI Max/Min, Total Hear Beats: str({rows})"
        Plots.group_hr_distribution(sqi_ibi_ratio, bins = 50, title_append=plot_txt)

    # Compute Pulse Wave Features (pwf)
    pwf = PulseWaveFeatures(data) 
    data, beat_features = pwf.compute()
    for i in range( 2600, 2700, 1):
        Plots.plot_beat_with_features_deriv(data, beat_features, i)
    breakpoint()

if __name__ == "__main__":
    main()
