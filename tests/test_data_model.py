import pytest
import pandas as pd

from data_model.sensor_data import SensorData
from data_model.condition import Condition
from data_model.subject import Subject
from data_model.subject_factory import (
    create_subject_from_nested_dict,
    create_subjects_from_nested_dicts
)

# SensorData Tests
def test_sensor_data_get_data_and_repr():
    # Create a simple DataFrame for testing.
    data = pd.DataFrame({
        "time": [0, 1, 2],
        "value": [10, 20, 30]
    })
    sensor_type = "accelerometer"
    sensor_data = SensorData(sensor_type, data)
    
    # Check that get_data returns the same DataFrame.
    pd.testing.assert_frame_equal(sensor_data.get_data(), data)
    
    # Check __repr__ output contains the sensor type and number of rows.
    repr_str = repr(sensor_data)
    assert sensor_type in repr_str
    assert "rows=3" in repr_str

# Condition Tests
def test_condition_add_and_get_sensor_data():
    # Create two sensor data objects.
    df1 = pd.DataFrame({"a": [1, 2, 3]})
    df2 = pd.DataFrame({"b": [4, 5, 6]})
    
    sensor1 = SensorData("sensor1", df1)
    sensor2 = SensorData("sensor2", df2)
    
    condition = Condition("test_condition")
    
    # Add sensor data and test retrieval.
    condition.add_sensor_data(sensor1)
    condition.add_sensor_data(sensor2)
    
    retrieved_sensor1 = condition.get_sensor_data("sensor1")
    retrieved_sensor2 = condition.get_sensor_data("sensor2")
    
    pd.testing.assert_frame_equal(retrieved_sensor1.get_data(), df1)
    pd.testing.assert_frame_equal(retrieved_sensor2.get_data(), df2)
    
    # Test __repr__ includes condition name and sensor keys.
    repr_str = repr(condition)
    assert "test_condition" in repr_str
    assert "sensor1" in repr_str
    assert "sensor2" in repr_str

def test_condition_get_nonexistent_sensor_data():
    condition = Condition("empty_condition")
    # Attempt to retrieve a sensor that was never added should return None.
    assert condition.get_sensor_data("nonexistent") is None

# Subject Tests
def test_subject_add_and_get_condition():
    subject = Subject("subject_001")
    condition1 = Condition("rest")
    condition2 = Condition("exercise")
    
    subject.add_condition(condition1)
    subject.add_condition(condition2)
    
    retrieved_cond1 = subject.get_condition("rest")
    retrieved_cond2 = subject.get_condition("exercise")
    
    # Check that the conditions are correctly retrieved.
    assert retrieved_cond1 == condition1
    assert retrieved_cond2 == condition2
    
    # Check __repr__ includes subject id and condition names.
    repr_str = repr(subject)
    assert "subject_001" in repr_str
    assert "rest" in repr_str
    assert "exercise" in repr_str

def test_subject_get_nonexistent_condition():
    subject = Subject("subject_002")
    assert subject.get_condition("nonexistent") is None

# Subject Factory Tests
@pytest.fixture
def sample_nested_dict():
    # Create sample data for one subject with two conditions and two sensors per condition.
    df_acc = pd.DataFrame({"acc_x": [0.1, 0.2], "acc_y": [0.3, 0.4]})
    df_gyro = pd.DataFrame({"gyro_x": [1, 2], "gyro_y": [3, 4]})
    return {
        "condition1": {
            "accelerometer": df_acc,
            "gyroscope": df_gyro,
        },
        "condition2": {
            "accelerometer": df_acc,
        }
    }

def test_create_subject_from_nested_dict(sample_nested_dict):
    subject_id = "subject_A"
    subject = create_subject_from_nested_dict(subject_id, sample_nested_dict)
    
    # Check subject id.
    assert subject.subject_id == subject_id
    
    # Check conditions.
    cond1 = subject.get_condition("condition1")
    cond2 = subject.get_condition("condition2")
    assert cond1 is not None
    assert cond2 is not None
    
    # Check sensors in condition1.
    sensor_acc = cond1.get_sensor_data("accelerometer")
    sensor_gyro = cond1.get_sensor_data("gyroscope")
    pd.testing.assert_frame_equal(sensor_acc.get_data(), sample_nested_dict["condition1"]["accelerometer"])
    pd.testing.assert_frame_equal(sensor_gyro.get_data(), sample_nested_dict["condition1"]["gyroscope"])
    
    # Check sensors in condition2.
    sensor_acc2 = cond2.get_sensor_data("accelerometer")
    pd.testing.assert_frame_equal(sensor_acc2.get_data(), sample_nested_dict["condition2"]["accelerometer"])

def test_create_subjects_from_nested_dicts(sample_nested_dict):
    # Create nested dict for multiple subjects.
    all_data = {
        "subject_A": sample_nested_dict,
        "subject_B": {
            "conditionX": {
                "sensorX": pd.DataFrame({"x": [10, 20]}),
            }
        }
    }
    
    subjects = create_subjects_from_nested_dicts(all_data)
    
    # Check that we have two subjects.
    assert len(subjects) == 2
    
    # Check subject IDs.
    subject_ids = {subject.subject_id for subject in subjects}
    assert "subject_A" in subject_ids
    assert "subject_B" in subject_ids

    # Further check one subject's condition and sensor data.
    subject_a = next(s for s in subjects if s.subject_id == "subject_A")
    cond1 = subject_a.get_condition("condition1")
    assert cond1 is not None
    sensor_acc = cond1.get_sensor_data("accelerometer")
    pd.testing.assert_frame_equal(sensor_acc.get_data(), sample_nested_dict["condition1"]["accelerometer"])
