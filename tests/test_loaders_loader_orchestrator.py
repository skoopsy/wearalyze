import pytest
import os
from unittest.mock import patch, MagicMock

from src.data_model.study_data import StudyData, Subject, SessionData
from src.loaders.loader_orchestrator import LoaderOrchestrator

@pytest.fixture
def example_config():
    """
    Provide a sample config dict that aligns with LoaderOrchestrator's expectations.
    Adjust values as needed for your actual environment / tests.
    """
    return {
        "data_source": {
            "subjects_dir": "/fake/path/subjects",
            "subjects_to_load": ["all"],  # can be ["all"] or a list of subject IDs
            "multi_condition": {
                "conditions": ["rest", "exercise"]  # sessions to be loaded for each subject
            },
            "sensor_type": ["ppg", "acc"],  # sensor types to load
            "device": "some_device"
        }
    }

@pytest.fixture
def orchestrator(example_config):
    """
    Returns an instance of LoaderOrchestrator using the example config.
    """
    return LoaderOrchestrator(example_config)

# Testing 'subjects_to_load' = ["all"] with multiple subjects

@patch("os.listdir", return_value=["subject01", "subject02", "not_a_dir.txt"])
@patch("os.path.isdir")
@patch("glob.glob")
@patch("src.loaders.loader_factory.DataLoaderFactory.get_loader")
def test_load_study_data_all_subjects(
    mock_get_loader, mock_glob, mock_isdir, mock_listdir, orchestrator, example_config
):
    """
    Test where 'subjects_to_load' is ['all'] and there are multiple subject dirs.
    We verify:
      - The orchestrator picks up subject01, subject02, ignoring non-directories.
      - Each subject has 2 sessions: rest, exercise
      - Each session loads sensor data for 2 sensors (ppg, acc)
      - standardise() is called only if data is not empty.
    """

    # Mock isdir to return True for subject dirs and session dirs,
    # ignoring the 'not_a_dir.txt'.
    def isdir_side_effect(path):
        if "not_a_dir.txt" in path:
            return False
        # If the path includes "rest" or "exercise", let's say it's valid
        if "rest" in path or "exercise" in path:
            return True
        # Otherwise, default to True for "subject01", "subject02"
        return True

    mock_isdir.side_effect = isdir_side_effect
    # Mock glob to return the same list of files for each session
    mock_glob.return_value = ["file1.csv", "file2.csv"]

    # Mock the loader
    loader_mock = MagicMock()
    # load_sensor_data returns a non-empty DataFrame-like object
    loader_mock.load_sensor_data.side_effect = [
        MagicMock(empty=False),  # subject01-rest ppg
        MagicMock(empty=False),  # subject01-rest acc
        MagicMock(empty=False),  # subject01-exercise ppg
        MagicMock(empty=False),  # subject01-exercise acc
        MagicMock(empty=False),  # subject02-rest ppg
        MagicMock(empty=False),  # subject02-rest acc
        MagicMock(empty=False),  # subject02-exercise ppg
        MagicMock(empty=False),  # subject02-exercise acc
    ]
    # standardise just returns a string or some placeholder
    loader_mock.standardise.side_effect = lambda sensor_type, df: f"std_{sensor_type}"

    mock_get_loader.return_value = loader_mock

    # Run
    study_data = orchestrator.load_study_data()

    # Check StudyData structure
    assert isinstance(study_data, StudyData)
    assert set(study_data.subjects.keys()) == {"subject01", "subject02"}

    subj1 = study_data.get_subject("subject01")
    subj2 = study_data.get_subject("subject02")
    assert subj1 is not None
    assert subj2 is not None

    # Each subject should have 'rest' and 'exercise' sessions
    assert set(subj1.sessions.keys()) == {"rest", "exercise"}
    assert set(subj2.sessions.keys()) == {"rest", "exercise"}

    # Check that each session has ppg and acc DataFrames
    sess_rest_subj1 = subj1.get_session("rest")
    assert "ppg" in sess_rest_subj1.sensors
    assert "acc" in sess_rest_subj1.sensors

    # Confirm load_sensor_data was called 8 times total
    # 2 subjects * 2 sessions * 2 sensor types = 8 calls
    assert loader_mock.load_sensor_data.call_count == 8

    # Confirm standardise() was also called 8 times
    assert loader_mock.standardise.call_count == 8


# Testing 'subjects_to_load' = ["specific_subject"]

@patch("os.path.isdir", return_value=True)
@patch("glob.glob", return_value=["file1.csv"])
@patch("src.loaders.loader_factory.DataLoaderFactory.get_loader")
def test_load_study_data_specific_subjects(
    mock_get_loader, mock_glob, mock_isdir, example_config
):
    """
    Test when 'subjects_to_load' is a specific list of subject IDs (not 'all').
    """
    example_config["data_source"]["subjects_to_load"] = ["subject42"]
    orchestrator = LoaderOrchestrator(example_config)

    loader_mock = MagicMock()
    loader_mock.load_sensor_data.return_value = MagicMock(empty=False)
    loader_mock.standardise.return_value = "std_ppg"
    mock_get_loader.return_value = loader_mock

    study_data = orchestrator.load_study_data()
    assert list(study_data.subjects.keys()) == ["subject42"]
    subject_obj = study_data.get_subject("subject42")
    assert subject_obj is not None
    # Should have "rest" and "exercise"
    assert set(subject_obj.sessions.keys()) == {"rest", "exercise"}


# Testing missing session directory

@patch("os.path.isdir")
@patch("glob.glob", return_value=["file1.csv"])
@patch("src.loaders.loader_factory.DataLoaderFactory.get_loader")
def test_missing_session_directory(
    mock_get_loader, mock_glob, mock_isdir, example_config
):
    """
    If the session directory doesn't exist, we skip it.
    """
    example_config["data_source"]["subjects_to_load"] = ["subject_missing"]
    example_config["data_source"]["multi_condition"]["conditions"] = ["rest", "exercise"]

    orchestrator = LoaderOrchestrator(example_config)

    def isdir_side_effect(path):
        # "rest" exists, "exercise" is missing
        if "exercise" in path:
            return False
        return True

    mock_isdir.side_effect = isdir_side_effect

    loader_mock = MagicMock()
    loader_mock.load_sensor_data.return_value = MagicMock(empty=False)
    mock_get_loader.return_value = loader_mock

    study_data = orchestrator.load_study_data()
    subject_obj = study_data.get_subject("subject_missing")
    # Only "rest" should appear since "exercise" is missing
    assert list(subject_obj.sessions.keys()) == ["rest"]


# Testing skip standardise() if DataFrame is empty
@patch("os.listdir", return_value=["subject01"])
@patch("os.path.isdir", return_value=True)
@patch("glob.glob", return_value=["file1.csv"])
@patch("src.loaders.loader_factory.DataLoaderFactory.get_loader")
def test_empty_dataframe_skips_standardise(
    mock_get_loader, mock_glob, mock_isdir, mock_listdir,  example_config
):
    """
    If loader.load_sensor_data returns an empty DataFrame, standardise() is NOT called.
    """
    orchestrator = LoaderOrchestrator(example_config)

    loader_mock = MagicMock()
    empty_df_mock = MagicMock()
    empty_df_mock.empty = True

    loader_mock.load_sensor_data.return_value = empty_df_mock
    loader_mock.standardise.side_effect = RuntimeError("Should not be called for empty dataframe.")
    mock_get_loader.return_value = loader_mock

    study_data = orchestrator.load_study_data()

    # No calls to standardise
    loader_mock.standardise.assert_not_called()

    # The subject/session structure should still be there
    assert len(study_data.subjects) > 0
    for sid in study_data.subjects:
        subj = study_data.get_subject(sid)
        for session_name, session_data in subj.sessions.items():
            for sensor_type, df in session_data.sensors.items():
                # They should all be empty
                assert df.empty


# Testing no subject directories found

@patch("os.path.isdir", return_value=False)
@patch("os.listdir", return_value=["some_file.txt", "another_file.csv"])
def test_no_subject_directories_found(
    mock_listdir, mock_isdir, example_config
):
    """
    If 'all' is requested but there's no valid directory (only files), 
    ensure we end up with an empty StudyData.
    """
    example_config["data_source"]["subjects_to_load"] = ["all"]
    orchestrator = LoaderOrchestrator(example_config)

    study_data = orchestrator.load_study_data()
    assert len(study_data.subjects) == 0, "No valid subject directories -> empty StudyData."
