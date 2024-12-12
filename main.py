from src.loaders.config_loader import get_config
from src.loaders.loader_factory import DataLoaderFactory

from src.preprocessors.ppg_preprocess import PPGPreProcessor

from src.processors.beat_detectors.factory import BeatDetectorFactory
from src.processors.sqi.beat_organiser import BeatOrganiser
from src.processors.biomarkers.basic_biomarkers import BasicBiomarkers
from src.processors.sqi.factory import SQIFactory

from src.visuals.plots import (plot_ppg_sections_vs_time,
                               plot_detected_inflections,
                               plot_scaleogram,
                               plot_signal_detected_peaks
                              )

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
        if verbosity >= 1: 
            print("Finished loading data")

        # Preprocess PPG data
        preprocessor = PPGPreProcessor(data, config)
        #TODO thresholding might not work for polar, only corsano:
        sections = preprocessor.create_thresholded_sections() # Get sections where device was worn
        
        # Degbugging prints
        if verbosity > 1:
            for i, section in enumerate(sections):
                print(f"Section {i+1} data points: {len(section)}") 
        
        # Apply bandpass filter - Creates new column 'filtered_value' in df
        preprocessor.filter_cheby2(sections)
        
        # Debugging prints
        if verbosity >= 1:
            print("Finished bandpass filtering  sections")
        
        # Plot entire compliance sections
        #plot_ppg_sections_vs_time(filtered_sections)

        # Detect heart beats
        beat_detector = BeatDetectorFactory.create(beat_detector_name)
        all_beats = []
        peak_indices = []
        trough_indices = []
        annotated_sections = [] # all sections stored
        
        for section_id, section in enumerate(sections):
                   
            # Detect "troughs" - Detects peaks, so the signal is inverted.
            signal = section.filtered_value * -1 # Invert sig for troughs
            detector_results = beat_detector.detect(signal)
            troughs = detector_results["peaks"]
            
            # Store trough indices independently
            trough_indices.extend(troughs) 

            # Flag troughs inplace
            section['is_beat_trough'] = False
            troughs_indices_realigned = section.iloc[troughs].index
            section.loc[troughs_indices_realigned, 'is_beat_trough'] = True
             
            # Plot detected peaks
            plot = False
            if plot:
                plt.plot(-1*signal.reset_index().filtered_value)
                plt.scatter(troughs, -1*signal.reset_index().filtered_value[troughs], color='red')
                plt.show()

            # In-place modification initialisation
            #section['section_id'] = section_id # logging of which section
            section['beat'] = -1 # Init at -1 incase row not allocated to beat
            section['is_beat_peak'] = False
         
            # Annotate beats and peaks
            for beat_id, (start, end) in enumerate(zip(troughs[:-1], troughs[1:])):
                # Assign beat number to rows
                section.loc[start:end, 'beat'] = beat_id
                
                # Find peak
                beat_data = section.iloc[start:end]
                peak_idx = beat_data['filtered_value'].idxmax()
                
                # Flag peak row for beat
                section.loc[peak_idx, 'is_beat_peak'] = True
                
                # Plot to check beat peaki
                #plt.plot(beat_data['filtered_value'])
                #plt.scatter(peak_idx, beat_data['filtered_value'][peak_idx], color='red')  
                #plt.show()
                #print(f"{beat_id}") 
            
            # Add annotated section to list
            annotated_sections.append(section)
            
            # Additonal storage of segmented beats incase needed
            segmented_beats = [
                section[section['beat'] == beat_id].copy() 
                for beat_id in section['beat'].unique() if beat_id != -1
            ]
            all_beats.extend(segmented_beats)
           
            # Debugging prints
            if verbosity >= 1:
                print(f"Section {section_id+1} / {len(sections)}")
     
            #TODO TO SPEED UP DEVELOPMENT, REMOVE IN PRO:
            #REMEMBER: This is only processing the first 2 sections
            # The other sections will still be present, just not processed!!
            #if section_id == 1:
            #    break
     
        # Combine anotated sections, may not need this atm 
        combined_sections = pd.concat(annotated_sections, ignore_index=True)
       
        # Create checkpoint - mostly for development
        # Save df as arrow fil
        if checkpoint_save:
            combined_sections.reset_index(drop=True).to_feather(checkpoint_file)
            print(f"Checkpoint created: combined_sections saved to {checkpoint_file}")
         
    if load_from_checkpoint and checkpoint_id == 1:
        combined_sections = pd.read_feather(checkpoint_file)
    
    #TODO Move this to visuals class as a plot method
    """
    # Plot combined sections
    plt.figure(figsize=(12, 6))
    plt.plot(combined_sections['filtered_value'], label='Filtered Signal', alpha=0.8)
    
    troughs = combined_sections.loc[combined_sections['is_beat_trough'] == True]
    plt.scatter(troughs.index, troughs['filtered_value'], color='blue', label='Troughs', s=15)

    peaks = combined_sections.loc[combined_sections['is_beat_peak'] == True]
    plt.scatter(peaks.index, peaks['filtered_value'], color='red', label='Peaks', s=15)

    plt.title("Combined Sections with Detected Troughs and Peaks")
    plt.xlabel("Index")
    plt.ylabel("Filtered Value")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()
    """
    # Visualise example beat
    #plt.plot(all_beats[100])
    #plt.show()

    #TODO Main issue - Investigate this:
    # len(combined_sections[combined_sections.is_beat_peak] == True) : 3645
    # len(n_beat_segments[n_beat_segments.is_beat_peak] == True) : 453
    breakpoint()
    # Organise beats into n-beat segments
    organiser = BeatOrganiser(group_size=sqi_group_size)
    n_beat_segments = organiser.group_n_beats_inplace(combined_sections)
    breakpoint() 
    # Calc some biomarker
    biomarkers = BasicBiomarkers(n_beat_segments)
    n_beat_segments_biomarkers = biomarkers.compute_ibi()
   
    breakpoint()
 
    # Compute SQI   
    sqi = SQIFactory.create_sqi(sqi_type=sqi_type, sqi_composite_details=sqi_composite_details)
    sqi_results = sqi.compute(n_beat_segments)
    
    breakpoint()
    #print(f"{len(sqi_results)} , {sqi_results[0]}") 

if __name__ == "__main__":
    main()
