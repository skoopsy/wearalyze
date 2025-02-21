import pytest
import pandas as pd
import os
from loaders.polar_verity_loader import PolarVerityLoader

# Create temp csv
@pytest.fixture


def temp_csv_file(tmp_path):
    content = """Phone timestamp;sensor timestamp [ns];channel 0;channel 1;channel 2;ambient
2024-03-13T04:05:34.771;763574775687450102;-1426;-4334;47386;-117294
2024-03-13T04:05:34.789;763574775654725806;-1451;-1216;42939;-117459
2024-03-13T04:05:34.807;763574775662001510;-1372;-3644;42938;-117768
2024-03-13T04:05:34.825;763574775531277214;-2435;-5699;40201;-118893
"""

    file_path = tmp_path / "test_file_PPG.txt"
    with open (file_path, "w") as f:
        f.write(content)
    return file_path

def config():
    return {
        "data_source": {
            "device": "polar-verity",
            "sensor": ["ppg"]
        },
        "filter": {
            "sample_rate": 100,
            "lowcut": 0.15,
            "highcut": 10,
            "order": 4
        },
        "ppg_preprocessing": {
            "threshold": 0,
            "min_duration": 30
        },

    }

def test_load_data(temp_csv_file):
    loader = PolarVerityLoader(config())
    data = loader.load_sensor_data('ppg',[temp_csv_file])
       
    # Verify data loaded as df
    assert isinstance(data, pd.DataFrame), "Data should be pandas df"

    # Verify structure of df
    expected_columns = [ "Phone timestamp", "sensor timestamp [ns]", 
                         "channel 0", "channel 1", "channel 2", "ambient"
                       ]
    assert list(data.columns) == expected_columns
    
def test_empty_file(tmp_path):
    empty_file = tmp_path / "empty_PPG.txt"
    empty_file.touch() # Create an empty file
    
    loader = PolarVerityLoader(config())
    with pytest.raises(pd.errors.EmptyDataError):
        loader.load_sensor_data('ppg',[empty_file])
    
def test_invalid_file_format(tmp_path):
    invalid_file = tmp_path / "invalid_PPG.txt"
    invalid_file.write_text("invalid data\nwithout proper columns\n")

    loader = PolarVerityLoader(config())
    with pytest.raises(ValueError):
        loader.load_sensor_data('ppg',[invalid_file])

def test_standardise(temp_csv_file):
    loader = PolarVerityLoader(config())
    raw_data = loader.load_sensor_data('ppg',[temp_csv_file])
    standardised_data = loader.standardise('ppg',raw_data)
    
    # Verify standardised data is in df
    assert isinstance(standardised_data, pd.DataFrame), "Standardised data must be in padnas dataframe"
    
    # Verify standardised structure
    expected_columns = ["phone_datetime","sensor_clock_ns",
                        "ppg_ch0", "ppg_ch1", "ppg_ch2", "ppg_amb",
                        "timestamp_ms", "ppg"]
    
    assert list(standardised_data.columns) == expected_columns, "Standardised data columns should match expected"
    
    # Verify standarised data content
    assert len(standardised_data) == 4, "Standardised data should have same number of rows as original"
    assert standardised_data["timestamp_ms"].iloc[0] == 763574775687.4501, "Timestamp must be converted to ms"
    expected_mean = (-1426 + -4334 + 47386)/3
    assert standardised_data['ppg'].iloc[0] == expected_mean, "Value should be the mean of channel 1, 2, and 3" 
