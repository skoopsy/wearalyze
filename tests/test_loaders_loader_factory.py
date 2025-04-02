import pytest
from loaders.loader_factory import DataLoaderFactory
from loaders.polar_verity_loader import PolarVerityLoader
from loaders.corsano_2872b_loader import Corsano2872bLoader

def config_polar():
    config = {"data_source": {
                "device": "polar-verity",
                "sensor_type": ["ppg"]
                }
             }
    return config

def config_corsano():
    config = {"data_source": {
                "device": "corsano-2872b",
                "sensor_type": ['ppg'],
                }
             }
    return config

def config_invalid():
    config = {"data_source": {
                "device": "intergalatic_gargle_blaster",
                "sensor_type": ['advanced_towels'],
                }
             }
    return config


def test_get_loader_polar_verity():
    loader = DataLoaderFactory.get_loader(config_polar())
    assert isinstance(loader, PolarVerityLoader), "Loader should be an instance of PolarVerityLoader"

def test_get_loader_corsano_2872b():
    loader = DataLoaderFactory.get_loader(config_corsano())
    assert isinstance(loader, Corsano2872bLoader), "Loader should be an instance of Corsano2872bLoader"

def test_get_loader_invalid_device():
    with pytest.raises(ValueError) as excinfo:
        DataLoaderFactory.get_loader(config_invalid())
        assert "Unsupported device unknown-device or sensor type PPG" in str(excinfo.value)

def test_get_loader_invalid_sensor_type():
    with pytest.raises(ValueError) as excinfo:
        DataLoaderFactory.get_loader(config_invalid())
        assert "Unsupported device polar-verity or sensor type Unknown" in str(excinfo.value)

