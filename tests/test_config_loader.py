import pytest
from unittest.mock import patch, MagicMock

import json
from src.loaders.config_loader import load_config_file, apply_arg_overrides, get_config

# Sample config data for tests

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

def test_load_config_file(tmp_path):
	""" Test loading configuration from JSON file """
	config_file = tmp_path / "config.json"
	config_file.write_test(json.dumps(SAMPLE_CONFIG))
	config = load_config_file(config_file)
	assert config == SAMPLE_CONFIG

def test_apply_arg_overrides():
	""" Test applying command-line overrides to config """
	args = MagicMock(
		file_paths=["new_path.csv"],
		device="new_device",
		sensor_type="new_sensor",
		threshold=2000
	)
	overridden_config = apply_arg_override(SAMPLE_CONFIG.copy(), args)

	assert overridden_config['data_source']['file_paths'] == ["new_path.csv"]
	assert overridden_config['data_source']['device'] == "new_device"
	assert overridden_config['data_source']['sensor_type'] == "new_sensor"
	assert overridden_config['ppg_preprocessing']['threshold'] == 2000

@patch("src.loaders.config_loader.get_arguments")
def test_get_config(mock_get_arguments, tmp_path):
	""" Test end-to-end config loading with command-line overrides """
	config_file = tmp_path / "config.json"
	config_file.write_text(json.dumps(SAMPLE_CONFIG))

	# Mock command-line arguments
	mock_get_arguments.return_value = MaficMock(
		config=str(config_file),
		file_paths=["new_path.csv"],
		device="new_device",
		sensor_type="new_sensor",
		threshold=2000,
	)

	config = get_config()
	assert config['data_source']['file_paths'] == ["new_path.csv"]
	assert config['data_source']['device'] == "new_device"
	assert config['data_source']['sensor_type'] == "new_sensor"
	assert config['ppg_preprocessing']['threshold'] == 2000
		
