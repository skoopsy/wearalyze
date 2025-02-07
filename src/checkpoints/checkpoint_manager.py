import pickle
import os

class CheckpointManager:
    """ Encapsulate checkpoint functionality with pickle. """

    def __init__(self, filename: str):
        self.filename = filename

    def save(self, data):
        directory = os.path.dirname(self.filename)
        if directory and not os.path.exists(directory):
            os.mkdirs(directory, exist_ok=True)
        with open(self.filename, "wb") as f:
            pickle.dump(data, f)
        print(f"Checkpoint saved: {self.filename}")

    def load(self):
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"Checkpoint file not found: {self.filename}")
        with open(self.filename, "rb") as f:
            data = pickle.load(f)
        print(f"Checkpoint loaded: {self.filename}")
        
        return data

    def exists(self):
        return os.path.exists(self.filename)
