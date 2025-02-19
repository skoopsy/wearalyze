from .subject import Subject
from .condition import Condition
from .sensor_data import SensorData

from typing import Dict, Any, List
import pandas as pd

def create_subject_from_nested_dict(subject_id: str, 
                            data: Dict[str, Dict[str, pd.DataFrame]]
) -> Subject:
    """
    Expected structure:

    { condition name: {
        sensor_type: pd.DataFrame,
        ...
        },
        ...
    }
    
    Args:
        subject_id (str): Unique identifier for the subject
        data (dict): Nested dict of conditions and sensor data
    Returns:
        Subject: populated subject instance
    """

    subject = Subject(subject_id)

    for condition_name, sensors_dict in data.items():
        condition = Condition(condition_name)
        
        for sensor_type, sensor_df in sensors_dict.items():
            sensor_data = SensorData(sensor_type, sensor_df)
            condition.add_sensor_data(sensor_data)
        
        subject.add_condition(condition)
    
    return subject

# Helper function to iterate over multiple subjects
def create_subjects_from_nested_dicts(all_data: Dict[str, Dict[str, Dict[ str, pd.DataFrame]]]) -> List[Subject]: 
    """
    Expected struct:

    { 
        subject_id: {
            condition_name: {
                sensor_type: pd.DataFrame,
                ...
            },
            ...
        },
        ...
    }

    Args:
        all_data (dict): Nested dict with all subjects and data
    Returns:
        List[Subjects]: List of subject instances
    """

    subjects = []
    for subject_id, subject_data in all_data.items():
        subject = create_subject_from_nested_dict(subject_id, subject_data)
        subjects.append(subject)
    
    return subjects

