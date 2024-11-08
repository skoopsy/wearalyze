import pandas as pd
import json
import os
from argparse import ArgumentParser

def load_ppg(file_path):
	"""Load PPG data from CSV"""
	return pd.read_csv(file_path)

def is_valid_file(parser, arg):
	if not os.path.exists(arg):
		parser.error(f"File '{arg}' does not exist!")
	else: 
		return arg

def parse_arguments():
	"""Parse command-line arguments"""

	parser = ArgumentParser(description="PPG file to process")

	parser.add_argument("-f", dest="file_name", required=True,
						help="Input file with PPG signal",
						metavar="--file",
						type=lambda x: is_valid_file(parser, x))
	parser.add_argument("-c", dest="config", required=True,
						help="Path to config file",
						metavar="--config",
						type=lambda x: is_valid_file(parser, x))

	return parser.parse_args() 	
