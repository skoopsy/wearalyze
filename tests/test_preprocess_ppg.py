import pytest
import pandas as pd
from datetime import timedelta
import numpy as np

from preprocessors.ppg_preprocess import PPGPreProcessor

@pytest.fixture
def sample_polar_data():
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2022-01-01 00:00:00', periods=100, freq='1s'),

        'timestamp_ms': np.linspace(0,40000,num=100), 
        'ppg': [10, 22, 21, 24, 25, 30, 60, 18, 15, 10] * 10
    })
    return data

@pytest.fixture
def sample_polar_config():
    return {
        'data_source': {
            'device': 'polar-verity',
            'sensor': ['ppg']
        },
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

def test_compliance_check_polar(sample_polar_data, sample_polar_config):
    preprocessor = PPGPreProcessor(sample_polar_data, sample_polar_config)
    sections = preprocessor.create_compliance_sections()
	
    #print(sections)

    assert len(sections) == 10
    assert sections[0]['ppg'].iloc[0] == 22

#TODO make cheby2 filter check, bit more complicated
