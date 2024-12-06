from src.loaders.config_loader import get_config
from src.loaders.loader_factory import DataLoaderFactory

from src.preprocessors.ppg_preprocess import PPGPreProcessor
from src.processors.beat_detector_msptd import beat_detect_msptd
from src.processors.beat_detector_ampd import peak_detect_ampd

from src.visuals.plots import plot_ppg_sections_vs_time, plot_detected_inflections, plot_scaleogram, plot_signal_detected_peaks

def main():
    # Parse cmd line args and load config
    config = get_config()

    # Extract config params - should make config a struct/obj
    file_paths = config['data_source']['file_paths']
    device = config['data_source']['device']
    sensor_type = config['data_source']['sensor_type']
    threshold = config['ppg_preprocessing']['threshold']

    # Load data
    loader = DataLoaderFactory.get_loader(device, sensor_type)
    data = loader.load_data(file_paths)
    data = loader.standardise(data)

    # Preprocess PPG data
    preprocessor = PPGPreProcessor(data, config)
    sections = preprocessor.create_thresholded_sections()
    filtered_sections = preprocessor.filter_cheby2(sections)

    # Plot entire compliance sections
    #plot_ppg_sections_vs_time(filtered_sections)

    # In place of for loop or vectorisation of all sections, 1 for development
    section = filtered_sections[-1].filtered_value * -1 # *-1 to invert signal to detect troughs

    # Run heart beat detector
    beat_detector = 'ampd'
    plot = True
    match beat_detector:
        case 'ampd':
            peaks, lms, gamma, lambda_scale = peak_detect_ampd(section)
            if plot:
                plot_signal_detected_peaks(section, peaks, beat_detector)
        
        case 'msptd': # Segment into individual pulse wave
            peaks, troughs, maximagram, minimagram = beat_detect_msptd(section,
                                                     'filtered_value',1000) 
            if plot:
                plot_detected_inflections(filtered_sections[0], peaks, troughs)
                plot_scaleogram(maximagram, 'Local maxima scaleogram')
                #plot_scaleogram(minimagram, 'Local minima scaleogram')

    # Segment into individual beats
    beats = []
    for i in range(len(peaks) - 1):
        start_idx = peaks[i]
        end_idx = peaks[i+1]
        beat = section.iloc[start_idx:end_idx].copy()
        beats.append(beat*-1) # Flip the beat back the right way up    

    import matplotlib.pyplot as plt
    plt.plot(beats[100])
    plt.show()
    
    # Group beats into n sized segments
    n_beat_segments = []
    n = 10
    for i in range(0, len(beats), n):
        segment = pd.concat(beats[i:i + 10])
        n_beat_segments.append(segment)

    # Run Signal quality indicies
    for i, segment in enumerate(n_beat_segments):
        print(f'Segment {i}, start:{segment['timestamp'].iloc[0]}')

if __name__ == "__main__":
    main()
