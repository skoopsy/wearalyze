import pytest
from unittest.mock import patch, MagicMock

from src.loaders.config_loader import get_config
import json
import os

def test_end_to_end_confi_loading(tmp_path):
	""" End-to-end test for loading config with overrides """
	
	# temporary config file
	SAMPLE_CONFIG = {
    	"data_source": {
        	"file_paths": ["default_path.csv"],
        	"device": "defualt_device",
        	"sensor_type": "default_sensor"
		},
    	"ppg_preprocessing": {
			"threshold": 10000
    	},
    	"filter": {
        	"lowcut": 0.15,
        	"highcut": 15,
        	"order": 4,
    	}
	}

	config_path = tmp_path / "config.json"
	with open(config_path, 'w') as f:
		json.dump(config_data, f)

	# Set up mock args
	with patch("src.utils.arg_parser.get_arguments") as mock_get_arguments:
		mock_get_arguments.return_value = MagicMock(
			config=str(config_path),
			file_paths=["new_path.csv"],
			device="new_device",
			sensor_type="new_sensor",
			threshold=2000,
		)

		# Load config with overrides applied
		config = get_config()

	assert config['data_source']['file_paths'] == ["new_paths.csv"]
	assert config['data_source']['device'] == "new_device"
	assert config['data_source']['sensor_type'] == 2000
	assert config['filter']['lowcut'] == 0.15
