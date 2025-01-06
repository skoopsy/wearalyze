import pytest
import pandas as pd
from loaders.corsano_2872b_loader import Corsano2872bLoader

# Fixture for creating a temporary valid CSV file
@pytest.fixture
def temp_csv_file(tmp_path):
    content = """timestamp,date,metric_id,chunk_index,quality,body_pose,led_pd_pos,offset,exp,led,gain,value
1730821062000,2024-11-05T15:37:42.000+00:00,0x7e,11,-1,1,6,0,0,52,2,45966
1730821062031,2024-11-05T15:37:42.031+00:00,0x7e,11,4,1,6,0,0,52,2,45966
1730821062062,2024-11-05T15:37:42.062+00:00,0x7e,11,4,1,6,0,0,52,2,10895
"""
    file_path = tmp_path / "test_file.csv"
    with open(file_path, "w") as f:
        f.write(content)
    return file_path

def test_load_data(temp_csv_file):
    loader = Corsano2872bLoader()
    data = loader.load_data([temp_csv_file])  # Pass list with one file

    # Verify that the data is loaded as a DataFrame
    assert isinstance(data, pd.DataFrame), "Data should be a pandas DataFrame"
    
    # Verify the structure of the DataFrame
    expected_columns = [
        "timestamp", "date", "metric_id", "chunk_index",
        "quality", "body_pose", "led_pd_pos", "offset",
        "exp", "led", "gain", "value"
    ]
    assert list(data.columns) == expected_columns, "Columns should match expected structure"

def test_empty_file(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.touch()  # Create an empty file
    
    loader = Corsano2872bLoader()
    with pytest.raises(pd.errors.EmptyDataError):
        loader.load_data([empty_file])

def test_invalid_file_format(tmp_path):
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("invalid data\nwithout proper columns\n")
    
    loader = Corsano2872bLoader()
    with pytest.raises(ValueError, match="missing required columns"):
        loader.load_data([invalid_file])

def test_standardise(temp_csv_file):
    loader = Corsano2872bLoader()
    raw_data = loader.load_data([temp_csv_file])
    standardised_data = loader.standardise(raw_data)
    
    # Verify standardised data is df
    assert isinstance(standardised_data, pd.DataFrame), "Standardised data must be in pandas Dataframe"
    
    # Verify structure
    expected_columns = [
        "datetime", "timestamp_ms", "ppg"
    ]
    assert list(standardised_data.columns) == expected_columns, f"Standardised columns should match expected structure: {standardised_data.columns}"

    # Verify that standardised data is correct
    assert len(standardised_data) == 3, "Standardised data should have same rows as original"
    assert standardised_data['timestamp_ms'].iloc[0] == 1730821062000, "Timestamp should be correctly retained"
    assert standardised_data['ppg'].iloc[0] == 45966, "PPG should match value"
