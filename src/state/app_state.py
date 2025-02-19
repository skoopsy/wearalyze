from src.loaders.loader_orchestrator import LoaderOrchestrator
from src.data_model.subject_factory import create_subjects_from_nested_dicts

class AppState:
    """
    Encapsulates the full state of the application, incl raw and processed data.

    It handles loading from a checkpoint, initialising a fresh state if needed, 
    and saving the state
    """
    def __init__(self, config, checkpoint_manager):
        self.config = config
        self.checkpoint = checkpoint_manager
        self.all_data = None
        self.subjects = None

    def load(self):
        """
        Load state from checkpoint
        """
        if self.checkpoint.get_load_status() and self.checkpoint.exists():
            print("[AppState] Loading state from checkpoint")
            state = self.checkpoint.load()
            self.all_data = state.get("all_data")
            self.subjects = state.get("subjects")
        else:
            print("[AppState] No valid checkpoint found; building fresh state")
            self.build_state()

        return self

    def build_state(self):
        """
        Build state by loading raw data and organising it into subjects
        Save state as checkpoint
        """
        load_orchestrator = LoaderOrchestrator(self.config)
        self.all_data = load_orchestrator.load_all()
        print("[AppState] Raw data loading complete")

        self.subjects = create_subjects_from_nested_dicts(self.all_data)
        print("[AppState] Subjects created")

        # Bundle state and save if checkpoint save status
        state = {
            "all_data": self.all_data,
            "subjects": self.subjects,
        }
        self.checkpoint.conditional_save_load(checkpoint_id=1, save_data=state)

    def get_subjects(self):
        """ Return subjects portion of state """
        if self.subjects is None:
            self.load()
        return self.subjects

    def get_raw_data(self):
        """ Return daw data portion of state """
        if self.all_data is None:
            self.load()
        return self.all_data
