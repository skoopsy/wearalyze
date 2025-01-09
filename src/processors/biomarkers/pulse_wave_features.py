import numpy as np
import pandas as pd

class PulseWaveFeatures:

    def __init__(self, data):
        # Time series df input
        self.data = data.copy()
    

    def compute(self):
        
        # Sort data, probably unnessicary
        self.data = self.data.sort_values(by=['global_beat_index','timestamp'])    
    
        # Compute in place on input df
        # signal derivatives
        self.first_derivative()
        self.second_derivative()
        self.third_derivative()

        # Build beat-level features df
        beats_features = self.create_beats_features()

        return self.data, beats_features


    def first_derivative(self):
        self.data['sig_1deriv'] = (
            self.data.groupby('global_beat_index')['filtered_value'].diff() 
        )


    def second_derivative(self):
        self.data['sig_2deriv'] = (
            self.data.groupby('global_beat_index')['first_derivative'].diff() 
        )
    

    def third_derivative(self):
        self.data['sig_3deriv'] = (
            self.data.groupby('global_beat_index')['second_derivative'].diff() 
        )


    def create_beats_features(self) -> pd.DataFrame:
        """
        Computes beat-level features added to a new output df where each row
        corresponds to a beat_id and each column is a feature/metric

        Args:
            self.data : pdDataFrame containing timeseries data for PPG
        
        Returns
            beats_features : pd.DataFrame
        """

        beats_features = []

        for beat_id, beat in self.data.groupby('global_beat_index'):
            
            beat_features = {'global_beat_index': beat_id}

            # Feature computations
            beat_features.update(self.compute_features_1deriv(beat))
            beat_features.update(self.compute_features_2deriv(beat))
            beat_features.update(self.compute_features_3deriv(beat))
            
            # Merge beat_dict into array with all beats 
            beats_features.append(beat_features)

        return pd.DataFrame(beats_features)
            
            
    def compute_features_1deriv(self, beat: pd.DataFrame) -> dict:
        
        # Zero-crossings
        cossing_indices = self.find_zero_crossings(beat["sig_1deriv"].values,
                                                   crossing_type="pos2neg"
                                                  )
        crossing_times = beat["timestamp"].iloc[crossing_indices].values

        feature_dict = {
            "1deriv_num_zero_crossing_pos2neg": len(crossing_times), 
            #TODO: Make this adative to the list size
            "1deriv_zero_crossing_1_idx": crossing_indices[0]
            }
        
        return feature_dict


    def compute_features_2deriv(self, beat: pd.DataFrame) -> dict:
        pass


    def compute_features_3deriv(self, beat: pd.DataFrame) -> dict:
        pass


    def find_zero_crossings(self, signal: np.ndarray, crossing_type: str) -> np.ndarray:
        """
        Returns the index of where a signal crosses zero in a specified 
        direction (from negative to positive, positive to negative, or both). 
        
        The returned index will be the data point before or at the zero
        point as opposed to the data point after the zero-crossing.

        Args:
            signal (np.ndarray): input a df[col].values
            crossing_type (str): Specify zero crossing direction: pos2neg
                                                                  neg2pos
                                                                  both
        
        Returns:
            zero_crossings (list(list)): List of zero crossing points with 
                                         index
        """    
        
        # Make sure input signal is in np.array form,  > will do it implicitly
        if not isinstance(signal, np.ndarray):
            signal = np.array(signal)
        
        pos = signal > 0
        npos = ~pos

        if crossing_type == "pos2neg":
            zero_crossings = np.where(pos[:-1] & npos[1:])[0]

        elif crossing_type == "neg2pos":
            zero_crossings = np.where(npos[:-1] & pos[1:])[0] 

        elif crossing_type == "both":
            zero_crossings = np.where.((pos[:-1] & npos[1:]) | (npos[:-1] & pos[1:]))[0]
        else:
            raise ValueError(f"Inalid crossing_type: {crossing_type}."
                              "Please use 'pos2neg', 'neg2pos', or 'both'."
                            )

        return zero_crossings

