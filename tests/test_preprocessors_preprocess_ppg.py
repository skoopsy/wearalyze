import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from src.preprocessors.ppg_preprocess import PPGPreProcessor

@pytest.fixture
def sample_corsano_data():
    """Sample df corsano device."""
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2022-01-01 00:00:00', periods=100, freq='1s'),
        'timestamp_ms': np.linspace(0, 2000, num=100), 
        'ppg': [10, 22, 21, 24, 25, 30, 60, 18, 15, 10] * 10
    })
    return data

@pytest.fixture
def sample_polar_data():
    """Sample df polar-verity device"""
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2022-01-01 00:00:00', periods=100, freq='1s'),
        'timestamp_ms': np.linspace(0, 2000, num=100), 
        'ppg': [10, -22, -21, -24, -25, -30, -60, -18, -15, 10] * 10
    })
    return data

@pytest.fixture
def sample_polar_config():
    """Configuration fixture incl filter &  device details."""
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
            'highcut': 9.0,
            'order': 4
        }
    }

@pytest.fixture
def single_section_df():
    """A single DataFrame 'section' with ascending timestamp_ms for resample/filter tests."""
    data_len = 30
    df = pd.DataFrame({
        'timestamp_ms': np.arange(data_len) * 100,
        'ppg': np.linspace(1,30, data_len)
    })
    return df

# Tests for create_compliance_sections
@patch("src.preprocessors.ppg_preprocess.ComplianceCheckFactory", autospec=True)
def test_create_compliance_sections_polar(mock_compliance_factory, sample_polar_data, sample_polar_config):
    """
    Test create_compliance_sections delegates to the compliance check method
    returned by ComplianceCheckFactory for the polar device.
    """
    mock_check_method = MagicMock()
    # Suppose the compliance method divides the data into 2 sections
    mock_check_method.create_compliance_sections.return_value = [
        sample_polar_data.iloc[:50],
        sample_polar_data.iloc[50:]
    ]
    # ComplianceCheckFactory.get_check_method(...) => mock_check_method
    mock_compliance_factory.get_check_method.return_value = mock_check_method

    preprocessor = PPGPreProcessor(sample_polar_data, sample_polar_config)
    sections = preprocessor.create_compliance_sections()

    # Verify we looked up the method for 'polar-verity'
    mock_compliance_factory.get_check_method.assert_called_once_with('polar-verity')
    # Ensure we called create_compliance_sections with the input data
    mock_check_method.create_compliance_sections.assert_called_once_with(sample_polar_data, sample_polar_config)

    # The result should be exactly what the mock returned
    assert len(sections) == 2
    assert len(sections[0]) == 50
    assert len(sections[1]) == 50

# Tests for compute_sample_freq
def test_compute_sample_freq_basic(sample_polar_data, sample_polar_config):
    """
    Test compute_sample_freq on a single 'section' list, verifying
    correct frequency calculation. pass only 1 section here.
    """
    # Setup
    preprocessor = PPGPreProcessor(sample_polar_data, sample_polar_config)
    # Our sections list has just 1 data chunk
    sections = [sample_polar_data.copy()]

    # The timestamps go from 0 to 40000 over 100 points => intervals ~ 404.04 ms
    # freq ~ 2.475... => round => 2.0 => final_freq=2.0 => interval_ms=500
    freq, interval_ms, interval_str = preprocessor.compute_sample_freq(sections)

    assert freq == 49.0  # because 100 points over 40000 ms
    assert interval_ms == 20.408
    assert interval_str == '20ms'

def test_compute_sample_freq_multiple_sections(sample_polar_data, sample_polar_config):
    """
    Test compute_sample_freq with multiple sections. Will be concatenated 
    internally for the median interval calc.
    """
    sec1 = sample_polar_data.iloc[:50].copy()
    sec2 = sample_polar_data.iloc[50:].copy()
    sections = [sec1, sec2]

    preprocessor = PPGPreProcessor(sample_polar_data, sample_polar_config)
    freq, interval_ms, interval_str = preprocessor.compute_sample_freq(sections)

    assert freq == 49.0
    assert interval_ms == 20.408
    assert interval_str == '20ms'

# Tests for resample
def test_resample_single_section(single_section_df, sample_polar_config):
    """
    Test resample() on a single section. resample from input_freq 
    down to resample_freq=5 Hz
    """
    preprocessor = PPGPreProcessor(single_section_df, sample_polar_config)

    sections = [single_section_df.copy()]
    resampled = preprocessor.resample(
        sections=sections,
        resample_freq=5,
        input_freq=10
    )

    assert len(resampled) == 1  # 1 output DataFrame
    out_df = resampled[0]

    assert len(out_df) == 15
    assert out_df['timestamp_ms'].iloc[-1] == 2800

def test_resample_multiple_sections(single_section_df, sample_polar_config):
    """
    Test resample() with 2 sections. Each is processed independently.
    """
    preprocessor = PPGPreProcessor(single_section_df, sample_polar_config)
    sec1 = single_section_df.iloc[:5].copy()   # 5 points
    sec2 = single_section_df.iloc[5:].copy()   # 5 points
    sections = [sec1, sec2]

    resampled = preprocessor.resample(sections, resample_freq=10, input_freq=10)
    assert len(resampled) == 2

# Tests for filter_cheby2
def test_filter_cheby2_basic(single_section_df):
    """
    Test filter_cheby2 on a single section. We supply a config 
    with the needed filter parameters.
    """
    config = {
        'data_source': {'device': 'polar-verity'},
        'filter': {
            'sample_rate': 100,
            'lowcut': 0.5,
            'highcut': 9.0,
            'order': 4
        }
    }

    preprocessor = PPGPreProcessor(single_section_df, config)

    sections = [single_section_df.copy(), single_section_df.copy()]
    sample_freq = 20 

    filtered = preprocessor.filter_cheby2(sections, sample_freq)

    assert len(filtered) == 2

    for i, out_sec in enumerate(filtered):
        assert 'timestamp_ms' in out_sec.columns
        assert 'filtered_value' in out_sec.columns
        assert len(out_sec) == len(single_section_df)
        assert out_sec['filtered_value'].dtype.kind in ('f', 'd')


