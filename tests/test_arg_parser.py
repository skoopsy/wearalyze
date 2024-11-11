from utils.arg_parser import get_arguments
import pytest
from unittest.mock import patch

def test_get_arguments():
	""" Test command-line argument parsing """
	test_args = [
		"main.py",
		"-f", "test_file.csv",
		"--device", "polar-verity",
		"--sensor_type", "PPG",
		"--threshold", "15000",
	]
	with patch("sys.argv", test_args):
		args = get_arguments()
		assert args.file_paths == ["test_file.csv"]
		assert args.device == "polar-verity"
		assert args.sensor_type == "PPG"
		assert args.threshold == 15000
