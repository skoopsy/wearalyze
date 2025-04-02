import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.pipelines.ppg_pipeline import PPGPipeline

@pytest.fixture
def mock_config():
    """
    Sample config that includes all keys needed by PPGPipeline
    and its dependencies.
    """
    return {
        "ppg_preprocessing": {
            "resample_freq": 50,
        },
        "ppg_processing": {
            "sqi_group_size": 5,
            "sqi_type": "simple_sqi",
            "sqi_composite_details": {},
        },
        "checkpoint": {
            "pipeline_ppg": {
                "save": True,
            }
        }
    }

@pytest.fixture
def empty_ppg_df():
    """Returns an empty DataFrame."""
    return pd.DataFrame()

@pytest.fixture
def nonempty_ppg_df():
    """Returns a minimal DataFrame with one column simulating PPG data."""
    return pd.DataFrame({"ppg_signal": [1, 2, 3, 4, 5]})

class TestPPGPipeline:
    @patch("src.pipelines.ppg_pipeline.CheckpointManager", autospec=True)
    def test_init(self, mock_checkpoint_mgr_cls, mock_config):
        """
        Test that PPGPipeline constructor sets self.config and
        initializes the CheckpointManager with config['checkpoint']['pipeline_ppg'].
        """
        pipeline = PPGPipeline(mock_config)
        
        # Check the pipeline references
        assert pipeline.config is mock_config
        mock_checkpoint_mgr_cls.assert_called_once_with(mock_config["checkpoint"]["pipeline_ppg"])
        assert pipeline.checkpoint == mock_checkpoint_mgr_cls.return_value

    @patch("src.pipelines.ppg_pipeline.PPGPreProcessor", autospec=True)
    @patch("src.pipelines.ppg_pipeline.CheckpointManager", autospec=True)
    def test_run_empty_df(
        self, mock_checkpoint_mgr_cls, mock_preprocessor_cls, mock_config, empty_ppg_df
    ):
        """
        Test run() with an empty PPG DataFrame. We expect it to return
        the same empty DataFrame and None, and skip all downstream processing.
        """
        pipeline = PPGPipeline(mock_config)
        out_data, out_features = pipeline.run(empty_ppg_df)

        # The pipeline should detect an empty DataFrame and return immediately
        assert out_data is empty_ppg_df
        assert out_features is None

        # Ensure no calls to PPGPreProcessor
        mock_preprocessor_cls.assert_not_called()
    
    @patch("src.pipelines.ppg_pipeline.CheckpointManager", autospec=True)    
    @patch("src.pipelines.ppg_pipeline.PPGPreProcessor", autospec=True)
    @patch("src.pipelines.ppg_pipeline.HeartBeatDetector", autospec=True)
    @patch("src.pipelines.ppg_pipeline.BasicBiomarkers", autospec=True)
    @patch("src.pipelines.ppg_pipeline.BeatOrganiser", autospec=True)
    @patch("src.pipelines.ppg_pipeline.SQIFactory", autospec=True)
    @patch("src.pipelines.ppg_pipeline.PulseWaveFeatures", autospec=True)
    def test_run_nonempty_df(
        self,
        mock_pwf_cls,
        mock_sqi_factory_cls,
        mock_beat_organiser_cls,
        mock_biomarkers_cls,
        mock_heartbeat_cls,
        mock_preprocessor_cls,
        mock_checkpoint_mgr_cls,
        mock_config,
        nonempty_ppg_df
    ):
        """
        Test run() with a non-empty DataFrame.
        Verify that each step is called in the correct order:
          1. _preprocess -> PPGPreProcessor
          2. _process_beats -> HeartBeatDetector
          3. _basic_biomarkers -> BasicBiomarkers
          4. _basic_sqi -> SQIFactory
          5. _pulse_wave_features -> PulseWaveFeatures
        Confirm the final return matches the last step's results.
        """
        # Mock instances returned by the classes
        mock_preproc_instance = mock_preprocessor_cls.return_value
        mock_heartbeat_instance = mock_heartbeat_cls.return_value
        mock_biomarkers_instance = mock_biomarkers_cls.return_value
        mock_sqi_instance = MagicMock(name="SQIInstance")
        mock_sqi_factory_cls.create_sqi.return_value = mock_sqi_instance
        mock_pwf_instance = mock_pwf_cls.return_value

        # Configure return values from each method to simulate pipeline flow
        # Preprocessing: returns "sections"
        mock_preproc_instance.create_compliance_sections.return_value = "sections"
        mock_preproc_instance.compute_sample_freq.return_value = (50, None, None)  # example
        mock_preproc_instance.resample.return_value = "resampled_sections"

        # HeartBeatDetector
        mock_heartbeat_instance.process_sections.return_value = ("combined_sections", "all_beats")
        
        # BeatOrganiser
        mock_organiser_instance = mock_beat_organiser_cls.return_value
        mock_organiser_instance.group_n_beats_inplace.return_value = "combined_sections"

        # BasicBiomarkers
        mock_biomarkers_instance.compute_ibi.return_value = "data_with_ibi"
        mock_biomarkers_instance.compute_bpm_from_ibi_group.return_value = "data_with_bpm"

        # SQIFactory -> .create_sqi(...) returns mock_sqi_instance
        mock_sqi_instance.compute.return_value = "sqi_results"

        # PulseWaveFeatures
        mock_pwf_instance.compute.return_value = ("final_data", "final_features")

        pipeline = PPGPipeline(mock_config)
        out_data, out_features = pipeline.run(nonempty_ppg_df)

        assert out_data == "final_data"
        assert out_features == "final_features"

        # Verify PPGPreProcessor usage
        mock_preprocessor_cls.assert_called_once_with(nonempty_ppg_df, mock_config)
        mock_preproc_instance.create_compliance_sections.assert_called_once()
        mock_preproc_instance.compute_sample_freq.assert_called_once_with("sections")
        mock_preproc_instance.resample.assert_called_once_with(
            sections="sections",
            resample_freq=mock_config["ppg_preprocessing"]["resample_freq"],
            input_freq=50
        )
        mock_preproc_instance.filter_cheby2.assert_called_once_with(
            "resampled_sections", mock_config["ppg_preprocessing"]["resample_freq"]
        )

        # Verify HeartBeatDetector usage
        mock_heartbeat_cls.assert_called_once_with(mock_config)
        mock_heartbeat_instance.process_sections.assert_called_once_with("resampled_sections")

        # Verify BasicBiomarkers usage
        mock_biomarkers_cls.assert_called_once_with("combined_sections")
        
        # Pipeline calls compute_ibi, compute_bpm_from_ibi_group, etc.
        mock_biomarkers_instance.compute_ibi.assert_called_once()
        mock_biomarkers_instance.compute_bpm_from_ibi_group.assert_called_once()
        mock_biomarkers_instance.compute_group_ibi_stats.assert_called_once()

        # Verify SQIFactory usage
        mock_sqi_factory_cls.create_sqi.assert_called_once_with(
            sqi_type=mock_config["ppg_processing"]["sqi_type"],
            sqi_composite_details=mock_config["ppg_processing"]["sqi_composite_details"],
        )
        mock_sqi_instance.compute.assert_called_once_with("data_with_bpm")

        # Verify PulseWaveFeatures usage
        mock_pwf_cls.assert_called_once_with("data_with_bpm")
        mock_pwf_instance.compute.assert_called_once()
