import pandas as pd

class BeatOrganiser:
    def __init__(self, group_size: int):
        self.group_size = group_size

    def group_n_beats(self, beats):
        """ Group beats into n-sized segments """
        
        n_beat_groups = [
            pd.concat(beats[i : i + self.group_size])
            for i in range(0, len(beats), self.group_size)
        ]

        return n_beat_groups
