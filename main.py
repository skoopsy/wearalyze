from src.loaders.config_loader import get_config 
from src.loaders.loader_factory import DataLoaderFactory

from src.preprocessors.ppg_preprocess import PPGPreProcessor
from src.processors.beat_detector_MSPTD import beat_detect_msptd
from src.visuals.plots import plot_ppg_sections_vs_time, plot_detected_inflections, plot_scaleogram

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

    # Preprocess PPG data
    preprocessor = PPGPreProcessor(data, config)
    sections = preprocessor.create_thresholded_sections()
    filtered_sections = preprocessor.filter_cheby2(sections)

    # Plot entire compliance sections
    #plot_ppg_sections_vs_time(filtered_sections)

    # Segment into individual pulse waves
    peaks, troughs, maximagram, minimagram = beat_detect_msptd(filtered_sections[10], 'filtered_value',1000)
    
    plot_detected_inflections(filtered_sections[0], peaks, troughs)
    plot_scaleogram(maximagram, 'Local maxima scaleogram')
    #plot_scaleogram(minimagram, 'Local minima scaleogram')

    # Run Signal quality indicies


if __name__ == "__main__":
    main()

