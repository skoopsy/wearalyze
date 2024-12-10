from src.loaders.config_loader import get_config
from src.loaders.loader_factory import DataLoaderFactory

from src.preprocessors.ppg_preprocess import PPGPreProcessor

from src.processors.beat_detectors.factory import BeatDetectorFactory
from src.processors.sqi.beat_organiser import BeatOrganiser
from src.processors.sqi.factory import SQIFactory

from src.visuals.plots import (plot_ppg_sections_vs_time,
                               plot_detected_inflections,
                               plot_scaleogram,
                               plot_signal_detected_peaks
                              )

import matplotlib.pyplot as plt
import pandas as pd

def main():
    # Parse cmd line args and load config
    config = get_config()

    # Extract config params
    #TODO Make this a struct and abstact unloading away
    verbosity = config['outputs']['print_verbosity']
    file_paths = config['data_source']['file_paths']
    device = config['data_source']['device']
    sensor_type = config['data_source']['sensor_type']
    threshold = config['ppg_preprocessing']['threshold']
    beat_detector_name = config["ppg_processing"]["beat_detector"]
    sqi_group_size = config["ppg_processing"]["sqi_group_size"]
    sqi_type = config["ppg_processing"]["sqi_type"]
    sqi_composite_details = config["ppg_processing"]["sqi_composite_details"]

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
            print(f"Section {i} data points: {len(section)}") 
    
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
    
    for i, section in enumerate(sections):
                
        # Detect "troughs" - This method detects peaks, so the signal is inverted.
        signal = section.filtered_value * -1 # Invert sig for trough detection 
        detector_results = beat_detector.detect(signal)
        troughs = detector_results["peaks"]

        # Segment into individual beats (Assume trough to trough is 1 beat)
        for j in range(len(troughs) - 1 ):
            start, end = troughs[j], troughs[j + 1]
            beat = signal.iloc[start:end].copy() * -1
            all_beats.append(beat)
            breakpoint() 
            # Find main peak per beat (remember it is inverted, so finding min)
            #TODO Set option to use basic idxmin OR use ampd again as idxmin might not be robust to noise 
            peak_idx = signal.iloc[start:end].idxmin()
            peak_indices.append(peak_idx)
        
        breakpoint()
        #TODO move into visuals module:
        """
        # Plot a sample beat with the detected peak
        plt.figure(figsize=(8, 4))
        idx = len(all_beats) // 2  # Take the middle beat for plotting
        beat_to_plot = all_beats[idx]
        peak_idx_to_plot = peak_indices[idx]

        # Plot the beat
        plt.plot(beat_to_plot.index, beat_to_plot, label="Beat Segment")
        # Highlight the peak
        plt.scatter(
            peak_idx_to_plot, beat_to_plot.loc[peak_idx_to_plot], 
            color="red", label="Detected Peak", zorder=5
        )
        plt.title("Example Beat with Detected Peak")
        plt.xlabel("Sample Index")
        plt.ylabel("PPG Signal Value")
        plt.legend()
        plt.grid(True)
        plt.show()
        """
        
        # Debugging prints
        if verbosity >= 1:
            print(f"Section {i+1} / {len(filtered_sections)}")
 
        
        #TODO TO SPEED UP DEVELOPMENT, REMOVE IN PROD
        if i == 1:
            break

    # Visualise example beat
    #plt.plot(all_beats[100])
    #plt.show()

    # Organise beats into n-beat segments
    organiser = BeatOrganiser(group_size=sqi_group_size)
    n_beat_segments = organiser.group_n_beats(all_beats)
    
    # Compute SQI   
    sqi = SQIFactory.create_sqi(sqi_type=sqi_type, sqi_composite_details=sqi_composite_details)
    sqi_results = [sqi.compute(segment) for segment in n_beat_segments]
    
    breakpoint()
    #print(f"{len(sqi_results)} , {sqi_results[0]}") 

if __name__ == "__main__":
    main()
