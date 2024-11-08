
from src.loaders.load_data import load_ppg, parse_arguments
from src.loaders.config import load_config
from src.preprocessors.ppg_preprocess import PPGPreProcessor
from src.visuals.plots import plot_ppg_sections_vs_time

def main():
	# Parse args and load config
	args = parse_arguments()
	config = load_config(args.config)
	
	# Load and preprocess PPG data
	data = load_ppg(args.file_name)
	preprocessor = PPGPreProcessor(data, config)
	sections = preprocessor.create_thresholded_sections()
	filtered_sections = preprocessor.filter_cheby2(sections)
	
	# Plot sections
	plot_ppg_sections_vs_time(filtered_sections)

if __name__ == "__main__":
	main()

