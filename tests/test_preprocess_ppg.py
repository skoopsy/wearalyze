import pytest
import pandas as pd
from datetime import timedelta
from preprocessors.ppg_preprocess import PPGPreProcessor

@pytest.fixture
def sample_data():
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2022-01-01 00:00:00', periods=100, freq='1s'),
        'ppg': [10, 22, 21, 18, 25, 30, 60, 18, 15, 10] * 10
    })
    data['timestamp_ms'] = pd.to_datetime(data['timestamp'], unit='ms')
    return data

@pytest.fixture
def sample_config():
    return {
        'ppg_preprocessing': {
            'threshold': 20,
            'min_duration': 1
        },
        'filter': {
            'sample_rate': 100,
            'lowcut': 0.5,
            'highcut': 10,
            'order': 4
        }
    }

def test_create_thresholded_sections(sample_data, sample_config):
    preprocessor = PPGPreProcessor(sample_data, sample_config)
    sections = preprocessor.create_thresholded_sections()
	
    #print(sections)

    assert len(sections) == 20
    assert sections[0]['data_points'].iloc[0] == 2
    assert sections[1]['data_points'].iloc[0] == 3

#TODO make cheby2 filter check, bit more complicated
