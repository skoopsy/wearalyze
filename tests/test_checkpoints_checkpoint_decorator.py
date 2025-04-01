from src.checkpoints.checkpoint_decorator import with_checkpoint

import pytest

# Dummy CheckpointManager
class DummyCheckpointManager:
    """
    You can configure its behavior by setting load_status, exists, etc.
    """
    def __init__(self, load_status=True, exists=True, load_return=None,
                 save_status=True, load_id=100, save_id=100):
        self._load_status = load_status
        self._exists = exists
        self._load_return = load_return
        self._save_status = save_status
        self._load_id = load_id
        self._save_id = save_id
        self.save_called_with = None

    def get_load_status(self) -> bool:
        return self._load_status

    def exists(self) -> bool:
        return self._exists

    def load(self):
        return self._load_return

    def get_load_id(self) -> int:
        return self._load_id

    def get_save_status(self) -> bool:
        return self._save_status

    def get_save_id(self) -> int:
        return self._save_id

    def save(self, data) -> None:
        self.save_called_with = data

# Dummy class with decorated method ---
class DummyComputation:
    def __init__(self, checkpoint_manager):
        # Decorator will use self.checkpoint
        self.checkpoint = checkpoint_manager
        self.called = False  # To track if the function is executed

    @with_checkpoint(checkpoint_id=100, stage_name="dummy_stage")
    def compute(self, x):
        self.called = True
        return x * 2


def test_decorator_load_checkpoint():
    """
    When a checkpoint exists, the decorator should load and return the 
    checkpointed value and the decorated function should not be executed.
    """
    dummy_cp = DummyCheckpointManager(
        load_status=True,
        exists=True,
        load_return="loaded_value",
        load_id=100,
        save_id=100
    )

    dummy = DummyComputation(dummy_cp)
    result = dummy.compute(5)
    assert result == "loaded_value"
    # Compute function should not have been called.
    assert dummy.called is False

def test_decorator_compute_and_save():
    """
    When no checkpoint exists, the decorated function should run and result
    saved.
    """
    dummy_cp = DummyCheckpointManager(
        load_status=True,
        exists=False,
        load_return="should_not_be_used",
        load_id=100,
        save_id=100
    )
    
    dummy = DummyComputation(dummy_cp)
    result = dummy.compute(5)
    assert result == 10
    assert dummy.called is True
    assert dummy_cp.save_called_with == 10

def test_decorator_load_disabled():
    """
    If load is disabled - decorated function should execute even if a 
    checkpoint file exists.
    """
    dummy_cp = DummyCheckpointManager(
        load_status=False,
        exists=True,         
        load_return="not_loaded",
        load_id=100,
        save_id=100
    )
    
    dummy = DummyComputation(dummy_cp)
    result = dummy.compute(5)
    assert result == 10
    assert dummy.called is True
    assert dummy_cp.save_called_with == 10
