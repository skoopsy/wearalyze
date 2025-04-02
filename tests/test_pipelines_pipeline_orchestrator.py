import pytest
from unittest.mock import patch, MagicMock
from src.pipelines.pipeline_orchestrator import PipelineOrchestrator
from src.data_model.study_data import StudyData

class FakeSession:
    """Container for session data used by the test."""
    def __init__(self):
        # Each session has dict of sensors (sensor_type -> DataFrame or any data)
        # and dict of processed results.
        self.sensors = {}
        self.processed = {}

class FakeSubject:
    """Container for subject data used by the test."""
    def __init__(self):
        # Each subject has dict of sessions (session_name -> FakeSession).
        self.sessions = {}

@pytest.fixture
def mock_study_data():
    """
    Creates a StudyData object with multiple subjects, each having multiple
    sessions with multiple sensors.
    """
    study_data = StudyData()

    # Suppose the StudyData has a .subjects dict: subject_id -> subject_data
    study_data.subjects["S1"] = FakeSubject()

    # Add two sessions: "session1", "session2"
    study_data.subjects["S1"].sessions["session1"] = FakeSession()
    study_data.subjects["S1"].sessions["session2"] = FakeSession()

    # For each session, add two sensor types: "ecg" and "ppg"
    ecg_data = MagicMock(name="ECGDataFrame")
    ppg_data = MagicMock(name="PPGDataFrame")

    study_data.subjects["S1"].sessions["session1"].sensors["ecg"] = ecg_data
    study_data.subjects["S1"].sessions["session1"].sensors["ppg"] = ppg_data
    study_data.subjects["S1"].sessions["session2"].sensors["ecg"] = ecg_data
    study_data.subjects["S1"].sessions["session2"].sensors["ppg"] = ppg_data

    return study_data


@pytest.fixture
def mock_config():
    """Returns configuration dict for the pipeline."""
    return {"pipeline_config_key": "some_value"}


class TestPipelineOrchestrator:
    def test_run_executes_valid_pipelines(self, mock_study_data, mock_config):
        """
        Test if a pipeline is returned for a sensor type, it is run,
        and processed results are stored in session_data.processed.
        """
        # Create mock pipeline that returns two placeholders for (processed_data, beat_features)
        mock_pipeline = MagicMock()
        mock_pipeline.run.return_value = ("mock_processed", "mock_features")

        # We'll mock PipelineFactory.get_pipeline so it always returns our mock_pipeline
        with patch("src.pipelines.pipeline_orchestrator.PipelineFactory", autospec=True) as mock_factory:
            mock_factory.get_pipeline.return_value = mock_pipeline

            orchestrator = PipelineOrchestrator(mock_study_data, mock_config)
            orchestrator.run()

        # Check that get_pipeline was called for each sensor type in each session
        # We have 2 sessions and 2 sensors in each => 4 calls total
        expected_calls = [
            # (sensor_type, config)
            ("ecg", mock_config),
            ("ppg", mock_config),
            ("ecg", mock_config),
            ("ppg", mock_config),
        ]
        actual_calls = [call.args for call in mock_factory.get_pipeline.call_args_list]
        assert actual_calls == expected_calls

        # Check that pipeline.run was called with the correct sensor data
        # The run method will be called 4 times total (since pipeline is always returned)
        # The sensor data is ecg_data, ppg_data for each of 2 sessions
        ecg_data = mock_study_data.subjects["S1"].sessions["session1"].sensors["ecg"]
        ppg_data = mock_study_data.subjects["S1"].sessions["session1"].sensors["ppg"]
        # We'll just confirm call args contain them
        run_call_args = [call.args for call in mock_pipeline.run.call_args_list]
        # We expect exactly 4 calls: (ecg_data), (ppg_data), (ecg_data), (ppg_data)
        assert run_call_args == [(ecg_data,), (ppg_data,), (ecg_data,), (ppg_data,)]

        # Verify that the processed results are stored in each session
        for session_name in ["session1", "session2"]:
            processed_dict = mock_study_data.subjects["S1"].sessions[session_name].processed
            assert processed_dict["ecg_processed"] == "mock_processed"
            assert processed_dict["ecg_features"] == "mock_features"
            assert processed_dict["ppg_processed"] == "mock_processed"
            assert processed_dict["ppg_features"] == "mock_features"

    def test_run_skips_none_pipelines(self, mock_study_data, mock_config):
        """
        Test that if PipelineFactory returns None for a sensor type,
        that sensor is skipped (no call to pipeline.run, no data stored).
        """
        # We'll simulate a scenario where:
        #  - "ecg" pipeline is valid
        #  - "ppg" pipeline is None (so it should be skipped)
        mock_ecg_pipeline = MagicMock()
        mock_ecg_pipeline.run.return_value = ("ecg_processed", "ecg_features")

        def mock_get_pipeline(sensor_type, config):
            if sensor_type == "ecg":
                return mock_ecg_pipeline
            else:
                return None

        with patch("src.pipelines.pipeline_orchestrator.PipelineFactory.get_pipeline", side_effect=mock_get_pipeline):
            orchestrator = PipelineOrchestrator(mock_study_data, mock_config)
            orchestrator.run()

        # Check the pipeline calls:
        # ecg is called 2 sessions => 2 times total
        assert mock_ecg_pipeline.run.call_count == 2

        # Check that ppg is skipped => no pipeline => no calls
        # Nothing to check on a None pipeline, but we can confirm no data stored in "ppg" keys
        for session_name in ["session1", "session2"]:
            processed_dict = mock_study_data.subjects["S1"].sessions[session_name].processed
            # ECG should be populated
            assert processed_dict["ecg_processed"] == "ecg_processed"
            assert processed_dict["ecg_features"] == "ecg_features"
            # PPG keys should not exist
            assert "ppg_processed" not in processed_dict
            assert "ppg_features" not in processed_dict
