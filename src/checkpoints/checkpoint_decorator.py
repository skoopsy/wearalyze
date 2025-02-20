from src.checkpoints.checkpoint_manager import CheckpointManager

from functools import wraps

def with_checkpoint(checkpoint_id: int, stage_name:str):
    """
    Decorator to wrap computations with load/save checkpoint logic.
    Using CheckpointManager via convention: self.checkpoint from decorator
    instance
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Try to load checkpoint
            cm: CheckpointManager = self.checkpoint
            if (cm.get_load_status() and
                cm.get_load_id() == checkpoint_id and
                cm.exists()
            ):
                print(f"[Checkpoint_dec] Loading checkpoint ID {checkpoint_id} for stage {stage_name}")
                
                return cm.load()

            # Run the wrapped function if can't load
            data = func(self, *args, **kwargs)

            # Save checkpoint if required
            if (cm.get_save_status() and
                cm.get_save_id() == checkpoint_id
            ):
                print(f"[Checkpoint_dec] Saving checkpoint ID {checkpoint_id}")
                cm.save(data)
            
            return data
        return wrapper
    return decorator
