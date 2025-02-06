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
            (pd.DataFrame, pd.DataFram):
                - self.data with additional columns
                - df of beat-level features (row per beat, col per feature set)
        """ 
        
        # Sort data, probably unnessicary
        self.data = self.data.sort_values(by=['global_beat_index','timestamp_ms'])    
         
        # Signal Smoothing        
        smooth = SignalSmoothing(self.data,
                                 signal_col="filtered_value",
                                 group_col="global_beat_index",
                                 output_col="sig_smooth"
        )
          
        smooth.group_apply(method="fda_bspline",
                           n_basis=21,
                           order=4
        )
        
        # Compute derivatives   
        calculator = DerivativesCalculator(self.data,
                                          "timestamp_ms", 
                                          "sig_smooth", 
                                          "global_beat_index"
        )
        calculator.compute_first_derivative()
        calculator.compute_second_derivative()
        calculator.compute_third_derivative()
        
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
            #beat_features.update(self.compute_features_misc(beat))
 
            # Merge beat_dict into array with all beats 
            beats_features.append(beat_features)

        return pd.DataFrame(beats_features)
            
    def compute_features_y(self, beat: pd.DataFrame) -> dict:
        
        # Systole
        # Reports relative idx of the beat
        systole_idx_local = beat['filtered_value'].values.argmax()
        # Reports df idx 
        systole_idx = beat['filtered_value'].idxmax()
        
        debug_plot = False
        if debug_plot == True:
            plt.plot(beat['filtered_value'])
            plt.scatter(systole_idx, beat['filtered_value'].loc[systole_idx])
            plt.show()

        systole_time = beat['timestamp_ms'].loc[systole_idx]
        
        # Beat duration
        beat_duration = beat['timestamp_ms'].iloc[-1] - beat['timestamp_ms'].iloc[0]
        
        feature_dict = {
            "y":{
                "systole": {
                    "idx": systole_idx_local,
                    "time": systole_time
                },
                "beat_duration": beat_duration 
            }
        }
        
        return feature_dict


    def compute_features_1deriv(self, beat: pd.DataFrame) -> dict:
        
        features_dict = {}

        # Max upslope of systole = ms
        if len(beat) < 2:
            ms_idx = None
            ms_idx_local = None
        else:
            try: 
                ms_idx = beat['sig_1deriv'].idxmax()
                ms_idx_local = np.nanargmax(beat['sig_1deriv']) # .values)
                features_dict.update({"ms": ms_idx_local})
            except ValueError:
                breakpoint()

        # Get zero crossings
        zero_cross = self._compute_zero_crossings_dict(beat, 
                                                       sig_name="sig_1deriv",
                                                       crossing_type="pos2neg"
        )
        features_dict.update({"zero_crossings": zero_cross})

        # Systolic Peak first p2n zero crossing after ms
        if zero_cross['sum'] > 0 and ms_idx_local is not None:
            # Pick from zross_cross if condition met 
            zc_after_ms = [zc_idx for zc_idx in zero_cross['idxs'] if zc_idx > ms_idx_local]
            
            if len(zc_after_ms) > 0:
                # 1st crossing after ms
                first_zc_idx_local = zc_after_ms[0]
                
                # Compute position from original zero_cross list for timestamp
                original_pos = zero_cross['idxs'].index(first_zc_idx_local)
                cross_time = zero_cross['times'][original_pos]

                systole = {
                    'detected': True,
                    'time': cross_time,
                    'idx': first_zc_idx_local
                }

                # Systolic crest time
                systole_crest_time_ms = systole['time'] = beat['timestamp_ms'].iloc[0]
                features_dict.update({
                    'systole': systole,
                    'systole_crest_time_ms': systole_crest_time_ms
                })
            else:
                # No zerocrossing after ms
                features_dict.update({'systole': {'detected': False}})
        else:
            features_dict.update({'systole': {'detected': False}})

        # Diastolic Peak: 2nd crosing after ms
        if zero_cross['sum'] > 1 and ms_idx_local is not None:
            # zc_after_ms should have been defined earlier, but just incase:
            zc_after_ms = [zc_idx for zc_idx in zero_cross['idxs'] if zc_idx > ms_idx_local]
            if len(zc_after_ms) >=2:
                second_zc_idx_local = zc_after_ms[1]
                original_pos_2 = zero_cross['idxs'].index(second_zc_idx_local)
                diastole_time = zero_cross['times'][original_pos_2]
            
                diastole = {
                    'detected': True,
                    'time': diastole_time,
                    'idx': second_zc_idx_local
                }
                features_dict.update({'diastole': diastole})
                
                # Systole-Diastole Delta Time
                if features_dict.get('systole', {}).get('detected', True): #TODO Check True or False?
                    deltaT = diastole_time - features_dict['systole']['time']
                    features_dict.update({'sys-dia-deltaT_ms': deltaT})
            else:
                features_dict.update({'diastole': {'detected': False}})
        else:
            features_dict.update({'diastole': {'detected': False}})

        return {'dydx': features_dict}
    
    #TODO: d2ydx2 features properly
    #TODO: workout how to get ms from dydx features
    def compute_features_2deriv(self, beat: pd.DataFrame) -> dict:
         
        features_dict = {}
        
        # Get zero crossings
        zero_cross = self._compute_zero_crossings_dict(beat,
                                                  sig_name="sig_2deriv",
                                                  crossing_type="both")
        features_dict.update({"zero_crossings": zero_cross})
 
        if zero_cross["sum"] > 4 : #TODO: This if is not needed as these points are not to do with zerocross
            
            features_dict.update({"abcde_detected": True})            
            
            # a wave - max d2ydx2 prior to ms from dydx
            a_wave = zero_cross['idxs'][0] # PLaceholder
            features_dict.update({"a_wave":a_wave})

            # b wave - first local minima after a
            b_wave = 1 # PLaceholder
            features_dict.update({"b_wave":b_wave})

            # c wave - greatest max between b and e, if no max then 1st of the 1st max on dydx after e or first min on d3ydx3 after e
            c_wave = 1 # Placeholder
            features_dict.update({"c_wave":c_wave})

            # d wave - lowest min on d2ydx2 after c and before e (if no minima then coincident with c)
            d_wave = 1 # Placeholder
            features_dict.update({"d_wave":d_wave})

            # e wave - 2nd maxima of d2ydx2 after ms and before 0.6T, unless c is inflection point, in which case take first maximum
            e_wave = 1 # PLaceholder
            features_dict.update({"e_wave":e_wave})

            # f wave - 1st local minium of d2ydx2 after e and before 0.8T
            f_wave = 1 # PLaceholder
            features_dict.update({"f_wave":f_wave})

        else:
            
            features_dict.update({"abcde_detected":False})
        """
        # Dicrotic notch
        if features_dict["abcde_detected"]: 
            dicrotic_notch = {"detected": True,
                              "time": e_wave["time"],
                              "idx": e_wave["idx"]}
          
        else: 
            dicrotic_notch = {"detected": False}
        
        # Diastole Location Estimate - When the diastolic peak is not present (such as in older subjects), the corresponding location of this point can be estimated as the first local maxima in the second derivative after the e- wave
        if zero_cross["sum"] > 5:
            diastole_estimate = {"detected": True,
                                 "time": zero_cross["times"][5],
                                 "idx":zero_cross["idxs"][5]}
        else: 
            diastole_estimate = {"detected": False}

        """ 
        # Assign to a value for combination into larger dict 
        features_dict_categorised = {
            "d2ydx2": features_dict
        }
       
        return features_dict_categorised


    def compute_features_3deriv(self, beat: pd.DataFrame) -> dict:
        
         
        features_dict = {}
        
        # Get zero crossings
        zero_cross = self._compute_zero_crossings_dict(beat,
                                                  sig_name="sig_3deriv",
                                                  crossing_type="both")
        features_dict.update({"zero_crossings": zero_cross})
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
       
        return features_dict_categorised 

    #4th deriv: https://pmc.ncbi.nlm.nih.gov/articles/PMC9280335/pdf/fpubh-10-920946.pdf
        # Early Systolic Component q1

        # Middle Systolic Components q2, q3
        
        # End Diastic component q4

 
    def compute_features_misc(self, beat: pd.DataFrame) -> dict:
        """
        Any features that require references from y, 1st, 2nd, 3rd derivative, 
        this should be run after those features have been computed
        """
        pass

        
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


    def _find_zero_crossings(self, signal: np.ndarray, crossing_type: str) -> np.ndarray:
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
   
