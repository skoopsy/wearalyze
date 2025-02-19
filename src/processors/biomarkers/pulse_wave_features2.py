import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .derivatives_calculator import DerivativesCalculator
from .signal_smoothing import SignalSmoothing

#TODO: Refactor into more classes PulseWaveFeatureOrchestrator,FeatureExtractor, ZeroCrossingAnalyser, 


class PulseWaveFeatures:
    """
    Class to orchestrate computation of PPG pulse-wave features including:
        - raw signal features (y)
        - first-derivative features (dydx)
        - second-derivative features (d2ydx2)
        - third-derivative features (d3ydx3)

    Attributes:
        data (pd.DataFrame): df with 'timstamp_ms', 'global_beat_index',
                            'filtered_value' columns
    """

    def __init__(self, data):
        # Time series df input
        self.data = data.copy()
    

    def compute(self):
        """
        Main pipeline to compute:
            - Smoothed signal via functional or smoothing methods
            - 1st, 2nd, & 3rd derivatives
            - Beat-level features / fiducials

        Returns:
            (pd.DataFrame, pd.DataFrame):
                - self.data: self.data with additional columns
                - beats_features: df of beat-level features (row per beat, col per feature set)
        """ 
        # Sort data just incase
        self.data = self.data.sort_values(by=['global_beat_index', 'timestamp_ms'])
        
        # Signal smoothing
        self._apply_signal_smoothing()
        
        # Compute derivatives
        self._compute_derivative()        
        
        # Built beat-level features dataframe
        beats_features = self.create_beats_features()

        return self.data, beats_features

    def _apply_signal_smoothing(self):
        """
        Smooth the signal for each beat using chosen method:
            - fda_bspline
            - rolling_avg
            - savitszky-golay
        
        Returns:
            Modifies the self.data df in place by adding the output column.

        """
        smoother = SignalSmoothing(
            data=self.data,
            signal_col="filtered_value",
            group_col="global_beat_index",
            output_col="sig_smooth"
        )
        
        # Apply smoothing on a beat by beat basis via groupby method
        smoother.group_apply(method="fda_bspline", b_basis=21, order=4)

    def _compute_derivatives(self):
        """
        Compute the 1st, 2nd, & 3rd derivatives of the smoothed signal
        
        Returns:
            Nothing, the columns are added inplace of the parent class self.data df
        """
        calculator = DerivativesCalculator( data = self.data,
                                            time_col = 'timestamp_ms',
                                            signal_col = 'sig_smooth',
                                            group_col = 'global_beat_index'
        )
        calculator.compute_first_derivative()
        calculator.compute_second_derivative()
        calculator.compute_third_derivative()

    def create_beats_features(self) -> pd.DataFrame:
        """
        Computes beat-level features and returns them in a new DataFrame

        Returns:
            pd.DataFrame: Each row is a beat_id, columns are feature dictionaries or features
        """
        all_beats_features = []

        for global_beat_index, beat_data in self.data.groupby('global_beat_index'):
            
            # Initiate features dict for beat
            beat_features = {'global_beat_index': global_beat_index}

            # Compute features
            y_features = self.compute_features_y(beat_data)
            dydx_features = self.compute_features_dydx(beat_data)
            d2ydx2_features = self.compute_features_d2ydx2(beat_data,
                                                           dydx_features
            )
            d3ydx3_features = self.compute_features_d3ydx3(beat_data,
                                                           dydx_features,
                                                           d2ydx2_features
            )
            
            # Collect in beat_features dict
            beat_features.update(y_features)
            beat_features.update(dydx_features)
            beat_features.update(d2ydx2_features)
            beat_features.update(d3ydx3_features)

            # Add beat features as row in beats_features            
            all_beats_features.append(beat_features)

        return pd.DataFrame(all_beats_features)


    def compute_features_y(self, beat: pd.DataFrame) -> dict:
        """
        Compute features from timeseries data that has been smoothed/filtered
        
        Args:
            beat (pd.DataFrame): data for current beat

        Returns:
            dict: {'y': {...}} containing features from y
        """
        #TODO: 'filtered_value' vs 'sig_smooth' - In one sense having systole from both is useful because it could be a way to validate the signal smoothing, although least squares does this better, the systole is the output so comparing outputs could be nice. Secondly, probably should incorperate a way to specify the input column to compute y features from.

        # Systolic peak
        systole_idx_local = beat['filtered_value'].values.argmax() # Argmax (local)
        systole_idx_global = beat['filtered_value'].idxmax() # Argmax (glbal df index) 
        systole_time = beat['timestamp_ms'].loc[systole_idx_global] #TODO: maybe this should be systole_time_global as global timstamp needed to comapre to the next beat, but there may be local time needed for other beat features, keep in mind for other feature computations later

        # Beat duration
        beat_duration = (
            beat['timestamp_ms'].iloc[-1] - beat['timestamp_ms'].iloc[0]
            if len(beat) > 1 else np.nan
        )

        feature_dict = {
            'y': {
                'systole': {
                    'idx_local': systole_idx_local,
                    'idx_global': systole_idx_global,
                    'time': systole_time
                },
                'beat_duration': beat_duration
            }
        }
        
        return feature_dict

    def compute_features_dydx(self, beat: pd.DataFrame) -> dict:
        """
        Compute features from the first derivative (dydx) of a PPG signal

        Args:
            beat (pd.DataFrame): data for current beat
        
        Returns:    
            dict: {'dydx':{...}} with dydx features.
        """
        features_dict = {}
        
        if len(beat) < 2:
            # Not enough points for useful derivative
            features_dict.update({
                'ms': None,
                'systole': {'detected': False},
                'diastole': {'detected': False}
            })
            return {'dydx': features_dict}

        # Feature: ms - Max upslope of systole index
        try:
            ms_idx_global = beat['sig_1deriv'].idmax()
            ms_idx_local = np.nanargmax(beat['sig_1deriv'].values)
            features_dict['ms'] = ms_idx_local
        except ValueError:
            # if values are NaN
            ms_idx_global = None
            ms_idx_local = None
            features_dict['ms'] = None

        # Compute zero-crossing points in dydx
        zero_cross = self._compute_zero_crossings_dict(
            beat, sig_name='sig_1deriv', crossing_type="pos2neg"
        )
        features_dict['zero_crossings'] = zero_cross

        # Feature: Systole - 1st p2n zero-crossing after ms
        if zero_cross['sum'] > 0 and ms_idx_local is not None:
            zc_after_ms = [zc for zc in zero_cross['idxs'] if zc > ms_idx_local]
            if len(zc_after_ms) > 0:
                first zc_idx_local = zc_after_ms[0]
                original_pos = zero_cross['idxs'].index(first_zc_idx_local)
                systole_time = zero_cross['times'][original_pos]

                features_dict['systole'] = {
                    'detected': True,
                    'time': systole_time,
                    'idx_local': first_zc_idx_local
                }
            else:
                features_dict['systole'] = {'detected': False}
        else:
            features_dict['systole'] = {'detected': False}

        # Feature: Diastole - 2nd p2n zero-crossing after ms
        if zero_cross['sum'] > 1 and ms_idx_local is not None:
            zc_after_ms = [zc for zc in zero_cross['idxs'] if zc > ms_idx_local]
            if len(zc_after_ms) >= 2:
                second_zc_idx_local = zc_after_ms[1]
                original_pos_2 = zero_cross['idxs'].index(second_zc_idx_local)
                diastole_time = zero_cross['times'][original_pos_2]

                features_dict['diastole'] = {
                    'detected': True,
                    'time': diastole_time,
                    'idx_local': second_zc_idx_local
                }

                # Systole-Diastole Delta Time
                if features_dict['systole']['detected']:
                    deltaT = diastole_time - feature_dict['systole']['time']
                    features_dict['sys-dia-deltaT_ms'] = deltaT
            else: 
                features_dict['diastole'] = {'detected': False}
        else:
            features_dict['diastole'] = {'detected': False}

        return {'dydx': features_dict}


    def compute_features_d2ydx2(self, 
                                beat: pd.DataFrame,
                                features_dydx: dict) -> dict:
        """
        Compute features from the second derivative (d2ydx2) of PPG like:
        a, b, c, d, e, & f waves. This uses fiducials from features calculated 
        from running compute_features_dydx() such as ms_idx.
        """
        features_dict = {}

        # Get ms_idx from dydx features
        ms_idx_local = features_dydx['dydx'].get('ms', None)
        deltaT = features_dydx['dydx'].get('sys-dia-deltaT_ms', None)

        # Compute zero-crossings, not sure if i need these yet
        zero_cross = self._compute_zero_crossings_dict( beat,
                                                        sig_name='sig_2deriv', 
                                                        crossing_type='both'
        )
        features_dict['zero_crossings'] = zero_cross

        # a wave - max d2ydx2 prior to ms from dydx
        
        # b wave - first local minima after a

        # c wave - greatest max between b and e, if no max then 1st of the 1st max on dydx after e or first min on d3ydx3 after e

        # d wave - lowest min on d2ydx2 after c and before e (if no minima then coincident with c)

        # e wave - 2nd maxima of d2ydx2 after ms and before 0.6T, unless c is inflection point, in which case take first maximum

        # f wave - 1st local minium of d2ydx2 after e and before 0.8T


        return {'d2ydx2': features_dict}


    def compute_features_d3ydx3(self, beat: pd.DataFrame) -> dict:
        
        features_dict = {}
        
         #TODO modify compute_zero_cross to label p2n and n2p in both method.


        # Early Systolic Component P0
        
        # Middle Systolic Component P1
        # p1 can be identified by searching for the first local maximum of the third derivative after the occurrence of the b-wave in the SDPPG,
        # The first local maximum of x′′′ after b. (10.1088/1361-6579/aabe6a)
 
        # Middle Systolic Component P2
        # a candidate p2 can be identified as the last local minimum of the third derivative before the d-wave, or as the local maximum of the original PPG between this candidate and the appearance of the dicrotic notch
        # Identify a candidate p2 at the last local minimum of x′′′ before d (unless c = d, in which case take the first local minimum of x′′′ after d). If there is a local maximum of x between this candidate and dic then use this instead. (10.1088/1361-6579/aabe6a)
        
        
        # End systolic component P3

        # Early Diastolic Component P4

         
        # Assign to a value for combination into larger dict 
        features_dict_categorised = {
            "d3ydx3": features_dict
        }
        
        return {'d3ydx3': features_dict}


    def compute_feautes_d4ydx4(self, beat: pd.DataFrame) -> dict:

        #4th deriv: https://pmc.ncbi.nlm.nih.gov/articles/PMC9280335/pdf/fpubh-10-920946.pdf
        features_dict = {}

        # Early Systolic Component q1

        # Middle Systolic Components q2, q3
        
        # End Diastic component q4

        return {'d4ydx4': features_dict}


    def _compute_zero_crossings_dict(self, beat: pd.DataFrame, sig_name: str, crossing_type: str) -> dict:
        """
        Uses _find_zero_crossings to collect zero corssing points and add to a
        nested dict

        Args:
            sig_name (str): df key for the signal column being analysed
            crossing_type (str): pos2neg, neg2pos, both
        Returns:
            feature_dict (dict): Nested dict of lists zero crossing points
        """
        # Zero-crossings
        zero_crossing_idxs = self._find_zero_crossings(beat[sig_name].values,
                                                   crossing_type=crossing_type
        )
        zero_crossing_times = beat["timestamp_ms"].iloc[zero_crossing_idxs].values


        # String shortening for dict key names 
        if crossing_type == "pos2neg":
            type_str = "p2n"
        elif crossing_type == "neg2pos":
            type_str = "n2p"
        elif crossing_type == "both":
            type_str = "both"
        else:
            ValueError(f"Invalid crossing_type: {crossing_type}")
         
        # Create dict with lists
        zero_crossings_dict = {
            "sum": len(zero_crossing_idxs),
            "type": type_str,
            "times": list(zero_crossing_times),
            "idxs": list(zero_crossing_idxs)
        }

        return zero_crossings_dict


    def _find_zero_crossings(self,
                             signal: np.ndarray,
                             crossing_type: str) -> np.ndarray:
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
        neg = ~pos

        if crossing_type == "pos2neg":
            zero_crossings = np.where(pos[:-1] & neg[1:])[0]

        elif crossing_type == "neg2pos":
            zero_crossings = np.where(neg[:-1] & pos[1:])[0] 

        elif crossing_type == "both":
            zero_crossings = np.where(
                (pos[:-1] & neg[1:]) | (neg[:-1] & pos[1:])
            )[0]
        else:
            raise ValueError(f"Invalid crossing_type: {crossing_type}."
                              "Please use 'pos2neg', 'neg2pos', or 'both'."
                            )

        return zero_crossings 
    
    
