from src.loaders.loader_orchestrator import LoaderOrchestrator
from src.checkpoints.checkpoint_manager import CheckpointManager
from src.data_model.study_data import StudyData

class AppState:
    """
    Encapsulates the full state of the application, incl raw and processed data.
    It handles loading from a checkpoint, initialising a fresh state if needed, 
    and saving the state
    """
    def __init__(self, config, checkpoint_config):
        self.config = config
        self.checkpoint = CheckpointManager(checkpoint_config)
        self.study_data = None

    def load(self) -> "AppState":
        """
        Load state from checkpoint, or 
        """
        if self.checkpoint.get_load_status() and self.checkpoint.exists():
            print("[AppState] Loading state from checkpoint")
            state = self.checkpoint.load()
            self.study_data = state.get("study_data")
        else:
            print("[AppState] No valid checkpoint found; building fresh state")
            self._build_state()

        return self

    def _build_state(self):
        """
        Build state by loading raw data and organising it into subjects
        Save state as checkpoint
        """
        load_orchestrator = LoaderOrchestrator(self.config)
        self.study_data = load_orchestrator.load_study_data()
        print("[AppState] Raw data loading complete")

        if self.checkpoint.get_save_status():
            self.checkpoint.save({"study_data": self.study_data})

    def get_study_data(self) -> StudyData:
        """ Return subjects portion of state """
        if self.study_data is None:
            self.load()
        return self.study_data

        
