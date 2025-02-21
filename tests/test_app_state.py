from src.state.app_state import AppState

import pytest

# Dummy implementations for testing
class DummyCheckpointManager:
    """
    A dummy checkpoint manager for testing. You can control whether it 
    simulates an existing checkpoint, and capture what is saved.
    """
    def __init__(self, load_status=True, exists=True, load_return=None, save_status=True):
        self._load_status = load_status
        self._exists = exists
        self._load_return = load_return or {}
        self._save_status = save_status
        self.save_called_with = None
        self._load_id = 1
        self._save_id = 1
        self._directory = "dummy_dir"
        self._data_id = "dummy_data_id"

    def get_load_status(self):
        return self._load_status

    def exists(self):
        return self._exists

    def load(self):
        return self._load_return

    def get_load_id(self):
        return self._load_id

    def get_save_status(self):
        return self._save_status

    def get_save_id(self):
        return self._save_id

    def get_load_path(self):
        return "dummy_load_path"

    def get_save_path(self):
        return "dummy_save_path"

    def save(self, data):
        self.save_called_with = data

    def conditional_save_load(self, checkpoint_id: int, save_data=None):
        if self.get_load_status() and self.get_load_id() == checkpoint_id and self.exists():
            return self.load()
        if self.get_save_status() and self.get_save_id() == checkpoint_id and save_data is not None:
            self.save(save_data)
        return save_data

# Dummy LoaderOrchestrator that returns a fixed raw-data dictionary.
class DummyLoaderOrchestrator:
    def __init__(self, config):
        self.config = config

    def load_all(self):
        return {"dummy": "raw_data"}

# Dummy subject factory function that returns a fixed list of subjects.
def dummy_create_subjects_from_nested_dicts(all_data):
    return ["subject1", "subject2"]


# Fixtures for config and monkeypatching
@pytest.fixture
def dummy_config():
    # Config dictionary with required keys for AppState
    return {
        "data_source": {"device": "dummy_device"},
        "checkpoint": {
            "global": {
                "load": {
                    "status": True,
                    "directory": "dummy_dir",
                    "checkpoint_id": 1,
                    "data_id": "dummy_data_id"
                },
                "save": {
                    "status": True,
                    "directory": "dummy_dir",
                    "checkpoint_id": 1,
                    "data_id": "dummy_data_id"
                }
            }
        }
    }


def test_load_from_checkpoint(dummy_config):
    """
    If a checkpoint exists, AppState.load() should load the saved state.
    """
    # Simulate a checkpoint that returns a known state.
    dummy_state = {"all_data": "loaded_all_data", "subjects": "loaded_subjects"}
    dummy_cp = DummyCheckpointManager(load_status=True, exists=True, load_return=dummy_state)
    app_state = AppState(dummy_config, dummy_cp)
    app_state.load()
    assert app_state.all_data == "loaded_all_data"
    assert app_state.subjects == "loaded_subjects"


def test_build_fresh_state(dummy_config, monkeypatch):
    """
    If no checkpoint exists, AppState should build a fresh state using 
    LoaderOrchestrator and subject factory.
    """
    # Dummy checkpoint manager that simulates no valid checkpoint.
    dummy_cp = DummyCheckpointManager(load_status=False, exists=False)
    # Monkeypatch LoaderOrchestrator and subject factory in AppState.
    monkeypatch.setattr("src.state.app_state.LoaderOrchestrator", DummyLoaderOrchestrator)
    monkeypatch.setattr("src.state.app_state.create_subjects_from_nested_dicts", dummy_create_subjects_from_nested_dicts)
    
    app_state = AppState(dummy_config, dummy_cp)
    app_state.load()
    # DummyLoaderOrchestrator returns {"dummy": "raw_data"}
    assert app_state.all_data == {"dummy": "raw_data"}
    # Dummy subject factory returns ["subject1", "subject2"]
    assert app_state.subjects == ["subject1", "subject2"]
    # Since saving is enabled, the checkpoint manager's save() should have been called.
    assert dummy_cp.save_called_with is not None


def test_get_subjects_and_raw_data(dummy_config, monkeypatch):
    """
    If subjects and raw data are not loaded, get_subjects() and get_raw_data()
    should trigger loading
    """
    dummy_cp = DummyCheckpointManager(load_status=False, exists=False)
    monkeypatch.setattr("src.state.app_state.LoaderOrchestrator", DummyLoaderOrchestrator)
    monkeypatch.setattr("src.state.app_state.create_subjects_from_nested_dicts", dummy_create_subjects_from_nested_dicts)
    
    app_state = AppState(dummy_config, dummy_cp)
    subjects = app_state.get_subjects()
    raw_data = app_state.get_raw_data()
    assert subjects == ["subject1", "subject2"]
    assert raw_data == {"dummy": "raw_data"}
