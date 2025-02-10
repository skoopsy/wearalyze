import pickle
import os

class CheckpointManager:
    """ Encapsulate checkpoint functionality with pickle. """

    def __init__(self, config: dict):
        if config:
            self.save_config = config["checkpoint"]["save"]
            self.load_config = config["checkpoint"]["load"]
        else:
            raise ValueError("Config must be provided")


    def save(self, data):

        directory = os.path.dirname(self.save_config.get("directory"))
        data_id = self.save_config.get("data_id")
        checkpoint_id = self.save_config.get("checkpoint_id")
        self.fpath = os.path.join(directory, f"{checkpoint_id}_{data_id}.pkl")

        if directory and not os.path.exists(directory):
            os.mkdirs(directory, exist_ok=True)

        with open(self.fpath, "wb") as f:
            pickle.dump(data, f)
        print(f"Checkpoint saved: {self.fpath}")


    def load(self):

        directory = os.path.dirname(self.load_config.get("directory"))
        data_id = self.load_config.get("data_id")
        checkpoint_id = self.load_config.get("checkpoint_id")
        self.fpath = os.path.join(directory, f"{checkpoint_id}_{data_id}.pkl")

        if not os.path.exists(self.fpath):
            raise FileNotFoundError(f"Checkpoint file not found: {self.fpath}")
        with open(self.fpath, "rb") as f:
            data = pickle.load(f)

        print(f"Checkpoint loaded: {self.fpath}")
        
        return data

    def exists(self):
        return os.path.exists(self.fpath)
