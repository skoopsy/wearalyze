import numpy as np
import pandas as pd

class PulseWaveFeatures:

    def __init__(self, data):
        # Time series df input
        self.data = data.copy()
    

    def compute(self):
        """
        Returns the full timeseries df with additional processing columns
        Returns a df of beat features per beat.
        """ 
        
        # Sort data, probably unnessicary
        self.data = self.data.sort_values(by=['global_beat_index','timestamp_ms'])    
    
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
            self.data.groupby('global_beat_index')['sig_1deriv'].diff() 
        )
    

    def third_derivative(self):
        self.data['sig_3deriv'] = (
            self.data.groupby('global_beat_index')['sig_2deriv'].diff() 
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

        for global_beat_index, beat in self.data.groupby('global_beat_index'):
            
            # Set the beat id for the beat being analysed
            beat_features = {'global_beat_index': global_beat_index}

            # Feature computations
            beat_features.update(self.compute_features_y(beat))
            beat_features.update(self.compute_features_1deriv(beat))
            beat_features.update(self.compute_features_2deriv(beat))
            beat_features.update(self.compute_features_3deriv(beat))
            
            # Merge beat_dict into array with all beats 
            beats_features.append(beat_features)

        return pd.DataFrame(beats_features)
            
    def compute_features_y(self, beat: pd.DataFrame) -> dict:
        
        # Systole
        systole_idx = beat['filtered_value'].idxmax()
        systole_time = beat['timestamp_ms'].iloc[systole_idx]
   
        feature_dict = {
            "systole_idx": systole_idx,
            "systole_time": systole_time
            }
        
        return feature_dict


    def compute_features_1deriv(self, beat: pd.DataFrame) -> dict:
        
        # Zero-crossings
        zero_crossing_idxs = self.find_zero_crossings(beat["sig_1deriv"].values,
                                                   crossing_type="pos2neg"
                                                  )
        zero_crossing_times = beat["timestamp_ms"].iloc[zero_crossing_idxs].values


        # Systole Location
        # Can just use this to confirm max of orig sig fiducial, ignore for now
        
        # String shortening for dict key names 
        if crossing_type == "pos2neg":
            type_str = "p2n"
        elif crossing_type == "neg2pos":
            type_str = "n2p"
        elif crossing_type == "both":
            type_str = ""
        else:
            ValueError(f"Invalid crossing_type: {crossing_type}")
         
        # Create feature dict with sum of zero-crossings:
        feature_dict = {
            f"1deriv_0cross_sum_{type_str}": len(zero_crossing_times), 
            }
        
        # Create dynamic dict key str based on num of zero_crossings
        names = []
        for idx, val in enumerate(zero_crossing_times):
            names.append(f"1deriv_0cross_{type_str}_{idx}")

        # Update feature dict with keys and values for zerocrossing.
        feature_dict.update(zip(names, zero_crossing_times))

        return feature_dict


    def compute_features_2deriv(self, beat: pd.DataFrame) -> dict:
        
        # a wave
        # b wave
        # c wave
        # d wave
        # e wave

        # dicrotic notch

        # Diastole Location
        # When the diastolic peak is not present (such as in older subjects), the corresponding location of this point can be estimated as the first local maxima in the second derivative after the e- wave


        pass


    def compute_features_3deriv(self, beat: pd.DataFrame) -> dict:
        
        # p1 can be identified by searching for the first local maximum of the third derivative after the occurrence of the b-wave in the SDPPG,
        
        # a candidate p2 can be identified as the last local minimum of the third derivative before the d-wave, or as the local maximum of the original PPG between this candidate and the appearance of the dicrotic notch
        

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
            zero_crossings = np.where((pos[:-1] & npos[1:]) | (npos[:-1] & pos[1:]))[0]
        else:
            raise ValueError(f"Invalid crossing_type: {crossing_type}."
                              "Please use 'pos2neg', 'neg2pos', or 'both'."
                            )

        return zero_crossings

