import json
from utils.arg_parser import get_arguments

def load_config_file(config_path):
	""" Loads config setting from JSON file """

	with open(config_path, 'r') as f:
		return json.load(f)

def apply_arg_overrides(config, args):
	""" Override configuration file values with command-line args """
	# Only override if argument is specified
	
	if args.file_paths:
		config['data_source']['file_paths'] = args.file_paths
	if args.device:
		config['data_source']['device'] = args.device
	if args.sensor_type:
		config['data_source']['sensor_type'] = args.sensor_type
	if args.threshold:
		config['ppg_preprocess']['threshold'] = args.threshold

	return config

def get_config():
	""" Main function to return the configuration with any overrides """
	
	args = get_arguments()
	config = load_config_file(args.config)
	config = apply_arg_overrides(config, args)
	
	return config
	
