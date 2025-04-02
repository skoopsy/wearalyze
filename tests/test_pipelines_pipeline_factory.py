import pytest
from unittest.mock import patch, MagicMock

from src.pipelines.pipeline_factory import PipelineFactory

@pytest.fixture
def mock_config():
    """A sample pipeline configuration."""
    return {
        "some_pipeline_setting": 123,
        "ppg_preprocessing": 100,
        "checkpoint": {"pipeline_ppg": True}
    }

class TestPipelineFactory:
    def test_get_pipeline_returns_ppg_pipeline(self, mock_config):
        """
        Ensures get_pipeline returns a mock PPG pipeline for 'ppg',
        without actually running PPGPipeline's real __init__.
        """
        mock_ppg_class = MagicMock(name="MockPPGClass")
        mock_ppg_instance = MagicMock(name="MockPPGInstance")
        mock_ppg_class.return_value = mock_ppg_instance

        # Patch the PipelineFactory's sensor dict so 'ppg' maps to our mock class
        with patch.dict(
            "src.pipelines.pipeline_factory.PipelineFactory.SENSOR_PIPELINES",
            {"ppg": mock_ppg_class},
            clear=True
        ):
            pipeline = PipelineFactory.get_pipeline("ppg", mock_config)

        mock_ppg_class.assert_called_once_with(mock_config)
        # The pipeline should be our mock instance
        assert pipeline is mock_ppg_instance

    def test_get_pipeline_unknown_sensor_returns_none(self, mock_config):
        """
        Ensures that if sensor_type isn't in SENSOR_PIPELINES, None is returned.
        """
        # Patch factory dict so it knows only about 'ppg' (and not 'ecg').
        with patch.dict(
            "src.pipelines.pipeline_factory.PipelineFactory.SENSOR_PIPELINES",
            {"ppg": MagicMock(name="SomeOtherMock")},
            clear=True
        ):
            pipeline = PipelineFactory.get_pipeline("ecg", mock_config)
            assert pipeline is None

    def test_get_pipeline_no_sensor_returns_none(self, mock_config):
        """Ensures that if sensor_type is None or empty, None is returned."""
        with patch.dict(
            "src.pipelines.pipeline_factory.PipelineFactory.SENSOR_PIPELINES",
            {"ppg": MagicMock(name="PPGMock")},
            clear=True
        ):
            pipeline_none = PipelineFactory.get_pipeline(None, mock_config)
            pipeline_empty = PipelineFactory.get_pipeline("", mock_config)

            assert pipeline_none is None
            assert pipeline_empty is None
