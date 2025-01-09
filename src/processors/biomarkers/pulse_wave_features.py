import numpy as np
import pandas as pd

class PulseWaveFeatures:
    def __init__(self, data):
        # Time series df input
        self.data = data.copy()
    
    def compute(self):
        
        # Sort data, probably unnessicary
        self.data = self.data.sort_values(by=['group_id','timestamp'])    
    
        # Compute in place on input df
        # derivatives
        self.first_derivative()
        self.second_derivative()
        self.third_derivative()

        # Extract features - unused stubs atm
        self.features_first_derivative()
        self.features_second_derivative()
        self.features_third_derivative()
        self.features_y()

        # Build beat-level features df
        beats_features = self.create_beats_features()

        return self.data, beats_features

    def first_derivative(self):
        self.data['sig_1deriv'] = (
            self.data.groupby('group_id')['filtered_value'].diff() 
        )

    def second_derivative(self):
        self.data['sig_2deriv'] = (
            self.data.groupby('group_id')['first_derivative'].diff() 
        )
    
    def third_derivative(self):
        self.data['sig_3deriv'] = (
            self.data.groupby('group_id')['second_derivative'].diff() 
        )

    def features_first_derivative(self):

        # Create boolian column to mark zero_crossing points
        #data.groupby('group_id')['first_derivative'].apply(process_beat_zero_crossings)
        
        #zero_crossing_rows = data[data['1stderiv_zero_crossing']]        
        
        # Systole - first zero crossing point
        # Should be after the first peak
        #systole_peak = 0       

        # Diastole Peak - Third zero crossing point
        # Shold be after the second peak
        #diastole_peak = 0
        pass

    def features_second_derivative(self):
        pass

    def features_third_derivative(self):
        pass

    def features_y(self):
        pass


    def create_beats_features(self) -> pd.DataFrame:
        """
        Computes beat-level features added to a new output df where each row
        corresponds to a beat_id and each column is a feature/metric

        Args:
            self.data : pdDataFrame containing timeseries data for PPG
        
        Returns
            beats_features : pd.DataFrame
        """

        # dict of nfeatures for each group_id
        beat_feature_rows = []

        # Group data into beats:
        for group_id, grp in self.data.groupby('group_id'):
            
            ## First Derivative ##
            #TODO: move this to first derivative features function and call here
            # Find zero-crossing indices            
            crossing_indicies = zelf.find_zero_crossings(
                grp['sig_1deriv'].values,
                crossing_type='both'
            )

            # Find zero-crossing timestamps
            crossing_times = grp['timestamp'].iloc[crossing_indicies].values

            # Store corossings
            row_dict = {
                'group_id': group_id,
                'num_zero_crossings': len(crossing_times)
            }
            
            # change this to be adative to number of zero-crossing times
            if len(crossing_time >= 1:
                row_dict['d1_cross_time_1'] = corssing_times[0]
            
            else: 
                row_dict['d1_cross_time_1'] = np.nan

        
            # Append dict to list
            beat_feature_rows.append(row_dict)
        
        beats_features = pd.DataFrame(beat_feature_rows)

        return beats_features


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

