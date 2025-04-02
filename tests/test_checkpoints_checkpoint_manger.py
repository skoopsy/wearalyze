from src.checkpoints.checkpoint_manager import CheckpointManager

import os
import pickle
import pytest

@pytest.fixture
def checkpoint_config(tmp_path):
    """ Config dict for checkpointing """
    return {
        "save": {
            "status": True,
            "checkpoint_id": 42,
            "directory": str(tmp_path / "checkpoints"),
            "data_id": "test_data"
        },
        "load": {
            "status": True,
            "checkpoint_id": 42,
            "directory": str(tmp_path / "checkpoints"),
            "data_id": "test_data"
        }
    }

@pytest.fixture
def dummy_data():
    """ Structure to checkpoint """
    return {"foo": "bar", "num": 123}

def test_get_paths(checkpoint_config, tmp_path):
    """ Check get_load_path and get_save_path produce the expected file path. """
    cm = CheckpointManager(checkpoint_config)
    expected_filename = f"{checkpoint_config['load']['checkpoint_id']}_{checkpoint_config['load']['data_id']}.pkl"
    expected_load_path = os.path.join(checkpoint_config["load"]["directory"], expected_filename)
    expected_save_path = os.path.join(checkpoint_config["save"]["directory"], expected_filename)
    assert cm.get_load_path() == expected_load_path
    assert cm.get_save_path() == expected_save_path

def test_save_and_load(tmp_path, checkpoint_config, dummy_data):
    cm = CheckpointManager(checkpoint_config)
    
    # Check no file exists initially.
    if os.path.exists(cm.get_save_path()):
        os.remove(cm.get_save_path())
    assert not cm.exists()

    # Save dummy data.
    cm.save(dummy_data)
    # Now file should exist.
    assert os.path.exists(cm.get_save_path())
    
    # Load data.
    loaded_data = cm.load()
    assert loaded_data == dummy_data

def test_exists(tmp_path, checkpoint_config, dummy_data):
    cm = CheckpointManager(checkpoint_config)
    
    # Initially, the file should not exist.
    assert not cm.exists()
    
    # Save dummy data.
    cm.save(dummy_data)
    assert cm.exists()

def test_conditional_save_load_load(tmp_path, checkpoint_config, dummy_data):
    """
    Test conditional_save_load when a checkpoint exists.
    First, manually save dummy_data so that exists() is True.
    Then conditional_save_load should load that data.
    """
    cm = CheckpointManager(checkpoint_config)
    
    # Ensure clean state.
    checkpoint_path = cm.get_save_path()
    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)
    
    # Save dummy data.
    cm.save(dummy_data)
    # conditional_save_load should detect an existing checkpoint and load it.
    result = cm.conditional_save_load(checkpoint_id=42, save_data={"should": "not be used"})
    # load enabled and file exists, result should equal dummy_data.
    assert result == dummy_data

def test_conditional_save_load_save(tmp_path, checkpoint_config, dummy_data):
    """
    Test conditional_save_load when no checkpoint exists. Set load status to 
    False: conditional_save_load should save the provided data.
    """
    # Copy config and set load status to False.
    config_modified = checkpoint_config.copy()
    config_modified["load"] = config_modified["load"].copy()
    config_modified["load"]["status"] = False

    cm = CheckpointManager(config_modified)

    # Ensure no file exists.
    checkpoint_path = cm.get_save_path()
    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)

    # Call conditional_save_load
    result = cm.conditional_save_load(checkpoint_id=42, save_data=dummy_data)
    # The save() method should return None.
    assert result is None

    # File should now exist and contain dummy_data.
    with open(checkpoint_path, "rb") as f:
        loaded = pickle.load(f)
    assert loaded == dummy_data

def test_invalid_config():
    # An empty config should raise a ValueError.
    with pytest.raises(ValueError):
        CheckpointManager({})
