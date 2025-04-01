import pytest
from unittest.mock import patch, MagicMock
from src.state.app_state import AppState
from src.data_model.study_data import StudyData


@pytest.fixture
def mock_config():
    return {"some_config_key": "some_config_value"}


@pytest.fixture
def mock_checkpoint_config():
    return {"checkpoint_path": "/fake/path/to/checkpoints"}


@pytest.fixture
def mock_checkpoint_manager():
    """
    Patches CheckpointManager at the class level, returning a tuple:
    (mock_checkpoint_manager_class, mock_checkpoint_manager_instance)
    """
    with patch("src.state.app_state.CheckpointManager", autospec=True) as mock_cls:
        mock_instance = mock_cls.return_value
        yield (mock_cls, mock_instance)


@pytest.fixture
def mock_loader_orchestrator():
    """
    Patches LoaderOrchestrator at the class level, returning a tuple:
    (mock_loader_orchestrator_class, mock_loader_orchestrator_instance)
    """
    with patch("src.state.app_state.LoaderOrchestrator", autospec=True) as mock_cls:
        mock_instance = mock_cls.return_value
        yield (mock_cls, mock_instance)


class TestAppState:
    def test_init_app_state(
        self,
        mock_config,
        mock_checkpoint_config,
        mock_checkpoint_manager  # (class, instance)
    ):
        """
        Test that AppState initializes correctly, creating a CheckpointManager
        and setting initial study_data to None.
        """
        mock_checkpoint_manager_class, mock_checkpoint_manager_instance = mock_checkpoint_manager

        app_state = AppState(mock_config, mock_checkpoint_config)

        # Check the constructor was called once with the checkpoint config
        mock_checkpoint_manager_class.assert_called_once_with(mock_checkpoint_config)

        # Check initial values
        assert app_state.config == mock_config
        assert app_state.study_data is None

    def test_load_from_checkpoint(
        self,
        mock_config,
        mock_checkpoint_config,
        mock_checkpoint_manager,
        mock_loader_orchestrator
    ):
        """
        Test that load() will retrieve data from an existing checkpoint if
        get_load_status and exists both return True, and does NOT build a fresh state.
        """
        _, mock_checkpoint_manager_instance = mock_checkpoint_manager
        mock_checkpoint_manager_instance.get_load_status.return_value = True
        mock_checkpoint_manager_instance.exists.return_value = True
        mock_checkpoint_manager_instance.load.return_value = {"study_data": "mocked_data"}

        _, mock_loader_orchestrator_instance = mock_loader_orchestrator

        app_state = AppState(mock_config, mock_checkpoint_config)
        result = app_state.load()

        # Verify checkpoint usage
        mock_checkpoint_manager_instance.get_load_status.assert_called_once()
        mock_checkpoint_manager_instance.exists.assert_called_once()
        mock_checkpoint_manager_instance.load.assert_called_once()

        # Verify we did NOT attempt to build a fresh state
        mock_loader_orchestrator_instance.load_study_data.assert_not_called()

        # AppState should now have the checkpoint's study_data
        assert result.study_data == "mocked_data"

    def test_load_fresh_state_if_no_checkpoint(
        self,
        mock_config,
        mock_checkpoint_config,
        mock_checkpoint_manager,
        mock_loader_orchestrator
    ):
        """
        Test that load() builds a fresh state if checkpoint is not available,
        or if get_load_status is False.
        """
        _, mock_checkpoint_manager_instance = mock_checkpoint_manager
        mock_checkpoint_manager_instance.get_load_status.return_value = False
        mock_checkpoint_manager_instance.exists.return_value = False

        mock_loader_orchestrator_class, mock_loader_orchestrator_instance = mock_loader_orchestrator
        mock_loader_orchestrator_instance.load_study_data.return_value = "fresh_mocked_data"

        app_state = AppState(mock_config, mock_checkpoint_config)
        result = app_state.load()

        mock_checkpoint_manager_instance.load.assert_not_called()

        mock_loader_orchestrator_class.assert_called_once_with(mock_config)
        mock_loader_orchestrator_instance.load_study_data.assert_called_once()

        assert result.study_data == "fresh_mocked_data"

    def test_build_state_saves_if_save_status_true(
        self,
        mock_config,
        mock_checkpoint_config,
        mock_checkpoint_manager,
        mock_loader_orchestrator
    ):
        """
        Test that _build_state saves to the checkpoint if get_save_status is True.
        """
        _, mock_checkpoint_manager_instance = mock_checkpoint_manager
        mock_checkpoint_manager_instance.get_save_status.return_value = True

        _, mock_loader_orchestrator_instance = mock_loader_orchestrator
        mock_loader_orchestrator_instance.load_study_data.return_value = StudyData()

        app_state = AppState(mock_config, mock_checkpoint_config)
        # Directly call the method to test its behavior
        app_state._build_state()

        # LoaderOrchestrator's load_study_data() should have been called
        mock_loader_orchestrator_instance.load_study_data.assert_called_once()

        # Because save_status is True, checkpoint.save(...) should be called
        mock_checkpoint_manager_instance.save.assert_called_once()
        call_args = mock_checkpoint_manager_instance.save.call_args[0][0]
        # We expect the "study_data" key to hold a StudyData object
        assert isinstance(call_args["study_data"], StudyData)

    def test_build_state_does_not_save_if_save_status_false(
        self,
        mock_config,
        mock_checkpoint_config,
        mock_checkpoint_manager,
        mock_loader_orchestrator
    ):
        """
        Test that _build_state does NOT save if get_save_status is False.
        """
        _, mock_checkpoint_manager_instance = mock_checkpoint_manager
        mock_checkpoint_manager_instance.get_save_status.return_value = False

        _, mock_loader_orchestrator_instance = mock_loader_orchestrator
        mock_loader_orchestrator_instance.load_study_data.return_value = StudyData()

        app_state = AppState(mock_config, mock_checkpoint_config)
        app_state._build_state()

        mock_checkpoint_manager_instance.save.assert_not_called()

    def test_get_study_data_calls_load_if_none(
        self,
        mock_config,
        mock_checkpoint_config,
        mock_checkpoint_manager,
        mock_loader_orchestrator
    ):
        """
        Test that get_study_data triggers a load() call if study_data is None.
        """
        _, mock_checkpoint_manager_instance = mock_checkpoint_manager
        # Turn off checkpoint load for simplicity
        mock_checkpoint_manager_instance.get_load_status.return_value = False
        mock_checkpoint_manager_instance.exists.return_value = False

        _, mock_loader_orchestrator_instance = mock_loader_orchestrator
        mock_loader_orchestrator_instance.load_study_data.return_value = "fresh_mocked_data"

        app_state = AppState(mock_config, mock_checkpoint_config)
        assert app_state.study_data is None

        data1 = app_state.get_study_data()
        data2 = app_state.get_study_data()

        # The first time, it triggers load() -> _build_state
        # The second time, it should just return the cached data
        assert data1 == "fresh_mocked_data"
        assert data2 == "fresh_mocked_data"

        # Confirm loader got called exactly once overall
        mock_loader_orchestrator_instance.load_study_data.assert_called_once()

    def test_get_study_data_returns_cached_if_not_none(
        self,
        mock_config,
        mock_checkpoint_config,
        mock_checkpoint_manager,
        mock_loader_orchestrator
    ):
        """
        Test that get_study_data returns the cached study_data without calling load()
        again if study_data is already set.
        """
        app_state = AppState(mock_config, mock_checkpoint_config)
        app_state.study_data = "already_loaded"

        returned_data = app_state.get_study_data()
        assert returned_data == "already_loaded"

        # Since study_data is not None, it should never call .load() on checkpoint
        # or try building a fresh state via LoaderOrchestrator.
        _, mock_checkpoint_manager_instance = mock_checkpoint_manager
        mock_checkpoint_manager_instance.get_load_status.assert_not_called()

        _, mock_loader_orchestrator_instance = mock_loader_orchestrator
        mock_loader_orchestrator_instance.load_study_data.assert_not_called()
