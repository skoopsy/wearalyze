from src.loaders.config_loader import get_config 
from src.loaders.loader_factory import DataLoaderFactory

from src.preprocessors.ppg_preprocess import PPGPreProcessor
from src.visuals.plots import plot_ppg_sections_vs_time

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
	plot_ppg_sections_vs_time(filtered_sections)
	
	# Segment into individual pulse waves
	#beat_detect_msptd()
	
	# Run Signal quality indicies
		

if __name__ == "__main__":
	main()

