from argparse import ArgumentParser

def get_arguments():
	"""Set up and parse command-line arguments"""
	
	parser = ArgumentParser(description="Wearalyse processing arguments")
	parser.add_argument("-c", "--config", type=str, default="config.json", help="Configuration file path")
	parser.add_argument("-f", "--file_paths", nargs='+', help="Override filepaths to input data to analyse from config")
	parser.add_argument("--device", type=str, help="Override device in config file (e.g. 'polarverity')")
	parser.add_argument("--sensor_type", type=str, help="Override sensor_type in config file (e.g 'PPG')")
	parser.add_argument("--threshold", type=float, help="Override threshold for data compliance segmenting")

	return parser.parse_args()

