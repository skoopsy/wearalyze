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

    file_path = tmp_path / "test_file.csv"
    with open (file_path, "w") as f:
        f.write(content)
    return file_path

def test_load_data(temp_csv_file):
    loader = PolarVerityLoader()
    data = loader.load_data([temp_csv_file])
       
    # Verify data loaded as df
    assert isinstance(data, pd.DataFrame), "Data should be pandas df"

    # Verify structure of df
    expected_columns = [
        "Phone timestamp", "sensor timestamp [ns]", "channel 0", "channel 1", "channel 2", "ambient", "timestamp"]
    assert list(data.columns) == expected_columns
    
    # Verifyy that timestamps are converted correctly
    assert data['timestamp'].iloc[0] == 763574775687.4501, "Timestamp conversion failed"
    
def test_empty_file(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.touch() # Create an empty file
    
    loader = PolarVerityLoader()
    with pytest.raises(pd.errors.EmptyDataError):
        loader.load_data([empty_file])
    
def test_invalid_file_format(tmp_path):
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("invalid data\nwithout proper columns\n")

    loader = PolarVerityLoader()
    with pytest.raises(ValueError):
        loader.load_data([invalid_file])
        