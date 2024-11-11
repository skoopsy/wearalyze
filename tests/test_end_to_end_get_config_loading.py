import pytest
from unittest.mock import patch, MagicMock

from loaders.config_loader import get_config
import json
import os

def test_end_to_end_config_loading(tmp_path):
	""" End-to-end test for loading config with overrides """
	
	# temporary config file
	SAMPLE_CONFIG = {
    	"data_source": {
        	"file_paths": ["default_path.csv"],
        	"device": "defualt_device",
        	"sensor_type": "default_sensor"
		},
    	"ppg_preprocess": {
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
		json.dump(SAMPLE_CONFIG, f)

	# Set up mock args
	with patch("sys.argv", ["main.py", "-c", str(config_path), "-f", "new_paths.csv", "--device", "new_device", "--sensor_type", "new_sensor", "--threshold", "2000"]):
		config = get_config()

	assert config['data_source']['file_paths'] == ["new_paths.csv"]
	assert config['data_source']['device'] == "new_device"
	assert config['data_source']['sensor_type'] == "new_sensor"
	assert config['ppg_preprocess']['threshold'] == 2000
	assert config['filter']['lowcut'] == 0.15
