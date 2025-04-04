import pickle
import os

class CheckpointManager:
    """ Encapsulate checkpoint functionality with pickle. """

    def __init__(self, config: dict):
        if not config:
            raise ValueError("Config must be provided")
        
        self.save_config = config["save"]
        self.load_config = config["load"]

    def get_load_status(self) -> bool:
        """
        Returns the status for loading from the config for conditional 
        checkpoitns
        """
        return self.load_config.get("status", False)

    def get_load_id(self) -> int:
        """
        Returns the load checkpoint_id from config for conditional checkpoints
        """
        return self.load_config.get("checkpoint_id")

    def get_save_status(self) -> bool:
        """
        Returns status for saving from config for conditional checkpoints
        """
        return self.save_config.get("status", False)

    def get_save_id(self) -> int:
        """
        Returns the save checkpoint_id from config for conditional checkpoints
        """
        return self.save_config.get("checkpoint_id")

    def get_load_path(self) -> str:
        """
        Returns full path of the checkpoint file for loading
        """
        directory = self.load_config.get("directory")
        data_id = self.load_config.get("data_id")
        checkpoint_id = self.get_load_id()
        
        return os.path.join(directory, f"{checkpoint_id}_{data_id}.pkl")

    def get_save_path(self) -> str:
        """
        Returns full path of checkpoint file for saving
        """
        directory = self.save_config.get("directory")
        data_id = self.save_config.get("data_id")
        checkpoint_id = self.get_save_id()

        return os.path.join(directory, f"{checkpoint_id}_{data_id}.pkl")

    def save(self, data) -> None:
        """ Save data to checkpoint file using config and pickle """

        if not self.get_save_status():
            print("[CheckpointManager] Checkpoint saving is disabled in config")
            return None
        
        save_path = self.get_save_path()
        directory = os.path.dirname(save_path)

        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(save_path, "wb") as f:
            pickle.dump(data, f)

        print(f"[CheckpointManager] Checkpoint saved: {save_path}")

    def load(self) -> None:
        """ Load data from checkpoint file using config and pickle """

        if not self.get_load_status():
            print("[CheckpointManager] Checkpoint loading is disabled in config['checkpoint']['load']['status']")
            return None

        load_path = self.get_load_path()

        if not os.path.exists(load_path):
            raise FileNotFoundError(f"[CheckpointManager] Checkpoint file not found: {load_path}")        

        with open(load_path, "rb") as f:
            data = pickle.load(f)

        print(f"[CheckpointManager] Checkpoint loaded: {load_path}")

        return data

    def exists(self) -> bool:
        """ Check if checkpoint file exists and checkpoint id matches """
        return os.path.exists(self.get_load_path())

    def conditional_save_load(self, checkpoint_id: int, save_data=None):
        """
        Handles conditional statment for load and save checking
        Replaces the need for repetative conditional statements for checking
        if need to load or save data, simply feed in the checkpoint id.
        """

        if self.get_load_status() and self.get_load_id() == checkpoint_id and self.exists():
            print(f"[CheckpointManager] Loading checkpoint {checkpoint_id}")
            return self.load()
    
        if self.get_save_status() and self.get_save_id() == checkpoint_id and save_data is not None:
            print(f"[CheckpointManager] Saving checkpoint {checkpoint_id}")
            return self.save(save_data)

        # This is a hack - if no checkpoint loaded, return input data
        return save_data
