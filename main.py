from src.loaders.config_loader import get_config
from src.loaders.loader_factory import DataLoaderFactory

from src.preprocessors.ppg_preprocess import PPGPreProcessor
from src.processors.beat_detectors.factory import BeatDetectorFactory

from src.visuals.plots import plot_ppg_sections_vs_time, plot_detected_inflections, plot_scaleogram, plot_signal_detected_peaks

import matplotlib.pyplot as plt
import pandas as pd

def main():
    # Parse cmd line args and load config
    config = get_config()

    # Extract config params - should make config a struct/obj
    file_paths = config['data_source']['file_paths']
    device = config['data_source']['device']
    sensor_type = config['data_source']['sensor_type']
    threshold = config['ppg_preprocessing']['threshold']
    beat_detector_name = config["ppg_processing"]["beat_detector"]

    # Load data
    loader = DataLoaderFactory.get_loader(device, sensor_type)
    data = loader.load_data(file_paths)
    data = loader.standardise(data) 
    print("Finished loading data")

    # Preprocess PPG data
    preprocessor = PPGPreProcessor(data, config)
    #TODO thresholding might not work for polar, only corsano:
    sections = preprocessor.create_thresholded_sections() # Get sections where device was worn
    for section in sections:
        print(f"{len(section)}")
     
    filtered_sections = preprocessor.filter_cheby2(sections)
    print("Finished bandpass filtering  sections")
    
    # Plot entire compliance sections
    #plot_ppg_sections_vs_time(filtered_sections)

    # Instantiate beat detector
    beat_detector = BeatDetectorFactory.create(beat_detector_name)
    
    all_beats = []
    # Process each section
    for i, section in enumerate(filtered_sections):
        signal = section.filtered_value * -1 # Invert sig for trough detection 
        
        # Detect "troughs"
        detector_results = beat_detector.detect(signal)
        print(f"{len(detector_results)}")
        peaks = detector_results["peaks"]
        # Segment into individual beat (trough to trough is 1 beat)
        beats = [
            signal.iloc[peaks[i] : peaks[i+1]].copy() * -1
            for i in range(len(peaks) -1)
        ]
        all_beats.extend(beats)
        print(f"Finished beat detection for section {i+1} / {len(filtered_sections)}")    
    # Visualise example beat
    plt.plot(all_beats[100])
    plt.show()

    # Group beats into n-sized segments
    n = 10
    n_beat_segments = [
        pd.concat(all_beats[i : i + n ])
        for i in range(0, len(all_beats), n)
    ]
    # Run Signal quality indicies
    for i, segment in enumerate(n_beat_segments):
        print(f'Segment {i}, start:{segment['timestamp'].iloc[0]}')

if __name__ == "__main__":
    main()
