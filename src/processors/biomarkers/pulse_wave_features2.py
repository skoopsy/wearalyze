from .derivatives_calculator import DerivativesCalculator
from .signal_smoothing import SignalSmoothing

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from abc import ABC, abstractmethod

class ZeroCrossingAnalyser:
    """
    Static methods for zero-crossing, local maxima, and minima calculations
    """

    @staticmethod
    def compute_zero_crossings(signal: np.adarray, 
                               timestamps: np.ndarray, 
                               crossing_type: str) -> dict:
        """
        Compute zero crossings for a given signal using boolean masks.

        Returns the index of where a signal crosses zero in a specified 
        direction (from negative to positive, positive to negative, or both). 
        
        The returned index will be the data point before or at the zero
        point as opposed to the data point after the zero-crossing.

        Args:
            signal (np.ndarray): Input signal
            timestamps (np.ndarray): Timestamps corresponding to the signal
            crossing_type (str): "pos2neg", "neg2pos", "both"

        Returns:
            dict: Contains the indices, times, and count of zero crossings
        """
         # Make sure input signal is in np.array form,  > will do it implicitly
        if not isinstance(signal, np.ndarray):
            signal = np.array(signal) 
        
        pos = signal > 0
        neg = ~pos

        if crossing_type == "pos2neg":
            idxs = np.where(pos[:-1] & neg[1:])[0]

        elif crossing_type == "neg2pos":
            idxs = np.where(neg[:-1] & pos[1:])[0] 

        elif crossing_type == "both":
            idxs = np.where((pos[:-1] & neg[1:]) | (neg[:-1] & pos[1:]))[0]
        
        else:
            raise ValueError(f"Invalid crossing_type: {crossing_type}."
                              "Please use 'pos2neg', 'neg2pos', or 'both'."
            )

        return {
            "sum": len(idxs),
            "type": crossing_type,
            "times": list(timestamps[idxs]),
            "idxs": list(idxs)
        }


    @staticmethod
    def local_maxima(signal: np.ndarray, 
                     prominence: float = 0.1, 
                     min_peak_dist: int = 1
    ) -> list:
        """
        Return max idxs from 1D signal using scipy find_peaks
        """ 
        peaks, _ = find_peaks(signal, prominence=prominence, distance=min_peak_dist)
        
        return peaks.tolist()


    @staticmethod
    def local_minima(signal: np.ndarray,
                     prominence: float = 0.1,
                     min_peak_dist: int = 1
    ) -> list:
        """
        Return min idxs from 1D signal using scipy find peaks
        """
        peaks, _ = find_peaks(-signal, prominence=prominence, distance=min_peak_dist)

        return peaks.tolist()


class FeatureExtractor(ABC):
    """
    Abstract base class for all the feature extraction classes here
    """
    
    @abstractmethod
    def compute_features(self, beat: pd.DataFrame, **kwargs) -> dict:
        """
        return features of beat
        """
        pass


class FeatureExtractorY(FeatureExtractor):
    """
    Extract features from time series PPG data that has been preprocessed
    and appropriately smoothed
    """
    
    #TODO: 'filtered_value' vs 'sig_smooth' - In one sense having systole from both is useful because it could be a way to validate the signal smoothing, although least squares does this better, the systole is the output so comparing outputs could be nice. Secondly, probably should incorperate a way to specify the input column to compute y features from.

    def compute_features(self, beat: pd.DataFrame, **kwargs) -> dict:
        features = {
            'systole': self._compute_systole(beat),
            'beat_duration': self._compute_beat_duration(beat)
        }

        return {'y': features}


    def _compute_systole(self, beat: pd.DataFrame) -> dict:
        """
        Compute systole peak information from ppg (y) vs time signal
        """
        systole_idx_local = int(np.argmac(beat['filtered_value'].values))
        systole_idx_global = beat['filtered_value'].idxmax()
        systole_timestamp_global = beat.loc[systole_idx_global, 'timestamp_ms']
        
        return {
            'idx_local': systole_idx_local,
            'idx_global': systole_idx_global,
            'time': systole_timestamp_global
        }


    def _compute_beat_duration(self, beat: pd.DataFrame) -> float:
        """
        Compute beat duration based on timestamp
        """

        if len(beat) > 1:
            return beat['timestamp_ms'].iloc[-1] - beat['timestamp_ms'].iloc[0]
        
        #else
        return np.nan


class FeatureExtractorDydx(FeatureExtractor):
    """
    Extract features from the first derivative (dydx) of a PPG signal
    """


    def compute_features(self, beat: pd.DataFrame, **kwargs) -> dict:
        features = {'detected': True}
        sig_dydx = beat['sig_1deriv']
        
        if len(beat) < 2 or sig_dydx.isna().sum() > 0.5 * len(sig_dydx):
            return {'dydx': self._set_features_not_detected()}

        features['zero_crossings'] = self._compute_zero_crossings(beat)
        features['ms'] = self._compute_feature_ms(sig_dydx)
        features['systole'] = self._compute_feature_systole(features, beat)
        features['diastole'] = self._compute_feature_diastole(features, beat)
        features['sys-dia-deltaT_ms'] = self._compute_feeature_sys_dia_deltaT_ms(features, beat)

        return {'dydx': features}


    def _set_features_not_detected(self) -> dict:
        return {
            'detected': False,
            'ms': None,
            'systole': {'detected': False}
            'diastole': {'detected': False}
        }
    

    def _compute_zero_crossings(self, beat: pd.DataFrame) -> dict:
        """
        Compute pos 2 neg zero crossings for 1st derivative
        """
        return ZeroCrossingAnalyser.compute_zero_crossings(
            signal=beat['sig_1deriv'].values,
            timestamps=beat['timestamp_ms'].values,
            crossing_type="pos2neg"
        )


    def _compute_feature_ms(self, sig) -> int:
        """
        ms = Max upslope gradient of the systole peak
        """ 
        ms_idx_local = np.nanargmax(sig_dydx.values)
        ms_idx_global = sig_dydx.idxmax() # Not used yet

        return ms_idx_local


    def _compute_feature_systole(self, features:dict, beat: pd.DataFrame) -> dict:
        """
        Systole - 1st p2n zero-crossing after ms feature        
        """
        zc = features['zero_crossings']
        ms = features['ms']

        zc_after_ms = [idx for idx in zc['idxs'] if idx > ms]
        if zc_after_ms:
            first_zc = zc_after_ms[0]
            position = zc['idxs'].index(first_zc)
        
            return {
                'detected': True
                'idx_local': first_zc,
                'time': zc['times'][position]
            }

        return {'detected': False}


    def _compute_feature_diastole(self, features: dict, beat: pd.DataFrame) -> dict:
        """
        Diastole - 2nd p2n zero-crossing after ms
        """
        zc = features['zero_crossings']
        ms = features['ms']
        zc_after_ms = [idx for idx in zc['idxs'] if idx > ms]
        if len(zc_after_ms) >= 2:
            second_zc = zc_after_ms[1]
            position = zc['idxs'].index(second_zc)

            return {
                'detected': True,
                'idx_local': second_zc,
                'time': zc['times'][position]
            }

        return {'detected': False}


    def _compute_feature_sys_dia_deltaT_ms(self, features: dict, beat: pd.DataFrame) -> dict:
        """
        sys-dia deltaT ms = time difference between systole and diastole peak
                            in miliseconds.
        """
        if features['systole'].get('detected') and features['diastole'].get('detected'):
            duration = features['diastole']['time'] - features['systole']['time']
            
            return {
                'detected': True
                'duration': duration
            }
                
        return {'detected': False}


class FeatureExtractorD2ydx2(FeatureExtractor):
    """
    Extract features from the second derivative (d2ydx2) of a PPG signal 
    """
    def compute_features(self, beat: pd.DataFrame, **kwargs) -> dict:
        # Get dydx features (prerequisit) - maybe try except
        dydx_features = kwargs.get('features_dydx'. {}).get('dydx', {})
        
        # Check ms exists otherwise cant do anything
        if dydx_features.get('ms') is None:
            return {'d2ydx2': {'detected': False}}
        
        # Set stuff, should these be instance variables? maybe
        features = {'detected': True}
        ms_idx_local = dydx_features['ms']
        sig_d2ydx2 = beat['sig_2deriv'].values
        #TODO: replace beat with timestamps = beat['timestamp_ms] as this is all that is extracted in below functs
    
        features['zero_crossings'] = ZeroCrossingAnalyser.compute_zero_crossings(
            signal=sig_d2ydx2,
            timestamp=beat['timestamp_ms'].values,
            crossing_type='both'
        )
        
        features['a_wave'] = self._compute_a_wave(beat, sig_d2ydx2, ms_idx_local)
        features['b_wave'] = self._compute_b_wave(beat, sig_d2ydx2, features['a_wave'])
        features['e_wave'] = self._compute_e_wave(beat, sig_d2ydx2, ms_idx_local)
        features['c_wave'] = self._compute_c_wave(beat, sig_d2ydx2, features['b_wave'], features['e_wave'])
        features['d_wave'] = self._compute_d_wave(beat, sig_d2ydx2, features['c_wave'], features['e_wave'])
        features['f_wave'] = self._compute_f_wave(beat, sig_d2ydx2, features['e_wave'])

        return {'d2ydx2': features}


    def _compute_a_wave(self, beat: pd.DataFrame, sig_d2ydx2: np.ndarray, ms_idx_local: int) -> dict:
        """
        a wave - Max d2ydx2 prior to ms from dydx
        """
        
        if ms_idx_local is not None and  ms_idx_local > 0:
            region = sig_d2ydx2[:ms_idx_local]
            peaks = ZeroCrossingAnalyser.local_maxima(region)
            if peaks:
                a_idx = int(peaks[np.argmax(region[peaks])])
                #TODO: Double check that the idx here is not shifted because dydx and d2ydx compared to y. Does it need padding? There will be NaNs
                return {
                    'detected': True,
                    'idx_local': a_idx,
                    'value': region[a_idx],
                    'time': beat['timestamp_ms'].iloc[a_idx]
                }
        
        return ('detected': False)

    def _compute_b_wave(self, beat: pd.DataFrame, sig_d2ydx2: np.ndarray, a_wave: dict) -> dict:
        """
        b wave - First local minima after a wave
        """
        
        if a_wave['detected'] is True and a_wave['idx_local'] < len(sig_d2ydx2) -1:
            region = sig_d2ydx2[a_wave['idx_local'] + 1:]
            minima = ZeroCrossingAnalyser.local_minima(region)
            if minima:
                idx_local = int(minima[0] + a_wave['idx_local'] + 1)

                return {
                    'detected': True,
                    'idx_local': idx_local,
                    'value': sig_d2ydx2[idx_local],
                    'time': beat['timestamp_ms'].iloc[idx_local]
                }

        return {'detected': False }


    def _compute_c_wave(self, beat: pd.DataFrame, sig_d2ydx2: np.ndarray, b_wave: dict, e_wave: dict) -> dict:
        """
        c wave - Greatest maxima between b-wave and e-wave, if no max then 1st
                 of the 1st max on dydx after e or first min on d3ydx3 after e
        """
    
        if b_wave['detected'] is True and e_wave['detected'] is True:
            start = b_wave['idx_local']
            end = e_wave['idx_local']
            region = sig_d2ydx2[start:end]

            if len(region) > 0:
                peaks = ZeroCrossingAnalyser.local_maxima(region)
                
                if peaks:
                    idx_local = int(peaks[np.argmax(region[peaks])] + start)

                    return {
                        'detected': True,
                        'idx_local': idx_local,
                        'value': sig_d2ydx2[idx_local],
                        'time': beat['timestamp_ms'].iloc[idx_local]
                    }

        return {'detected': False }


    def _compute_d_wave(self, beat: pd.DataFrame, sig_d2ydx2: np.ndarray, c_wave: dict, e_wave: dict) -> dict:
        """
        d wave - Lowest minima on s2ydx2 after c-wave and before e-wave.
                 If no minima then coincident with c-wave
        """
        if c_wave['detected'] is True and e_wave['detected'] is True:          
            start = c_wave['idx_local']
            end =  e_wave['idx_local']
            region = sig_d2ydx2[start:end]
            
            if len(region) > 0:
                minima = ZeroCrossingAnalyser.local_minima(region)
                
                if minima:
                    idx_local = int(minima[np.argmin(region[minima])] + start)
                    
                    return {
                        'detected': True,
                        'idx_local': idx_local,
                        'value': sig_d2ydx2[idx_local]
                        'time': beat['timestamp_ms'].iloc[idx_local]
                    }
            
        return {'detected': False}


    def _compute_f_wave(self, beat: pd.DataFrame, sig: np.ndarray, e_wave: dict) -> dict:
        """
        f wave - 1st local minimum of d2ydx2 after e and before 0.8T
        """
        #TODO: Add 0.8T check
        if e_wave['detected'] is True and e_wave['idx_local'] < len(sig_d2ydx2) -1:
            region = sig_d2ydx2[e_wave['idx_local'] + 1:]
            minima = ZeroCrossingAnalyser.local_minima(region)
            
            if minima:
                idx_local = int(minima[0] + e_wave['idx_local'] + 1)
                
                return {
                    'detected': True,
                    'idx_local': sig_d2ydx2[idx_local],
                    'time': beat['timestamp_ms'].iloc[idx_local]
                }        

        return {'detected': False}


class FeatureExtractorD3ydx3(FeatureExtractor):
    """
    Extract features from the third derivative (d3ydx3) of a PPG signal 
    """
    #TODO: Currently placehold stubs

    def compute_features(self, beat: pd.DataFrame, **kwargs) - > dict:
        features = {
            'p0': self._compute_p0(beat),
            'p1': self._compute_p1(beat),
            'p2': self._compute_p2(beat),
            'p3': self._compute_p3(beat),
            'p4': self._compute_p4(beat),
        }

    def _compute_p0(self, beat: pd.DataFrame):
        """
        p0 - Early systolic component
        """
        return None

    def _compute_p1(self, beat: pd.DataFrame):
        """
        p1 - Middle systolic component

        p1 can be identified by searching for the first local maximum of the 
        third derivative after the occurrence of the b-wave in the SDPPG, the 
        first local maximum of x′′′ after b. (10.1088/1361-6579/aabe6a)
        """
        return None

    def _compute_p2(self, beat: pd.DataFrame):
        """
        p2 - Middle systolic component

        A candidate p2 can be identified as the last local minimum of the third
        derivative before the d-wave, or as the local maximum of the original
        PPG between this candidate and the appearance of the dicrotic notch
        
        Identify a candidate p2 at the last local minimum of x′′′ before d 
        (unless c = d, in which case take the first local minimum of x′′′ 
        after d). If there is a local maximum of x between this candidate and 
        dic then use this instead. (10.1088/1361-6579/aabe6a)
        """
        return None

    def _compute_p3(self, beat: pd.DataFrame):
        """
        p3 - End Systolic Component
        """
        return None

    def _compute_p4(self, beat: pd.DataFrame):
        """
        p4 - Early diastolic component
        """
        return None


class FeatureExtractorD4ydx4(FeatureExtractor):
    """
    Extract features from the fourth derivative (d4ydx4) of a PPG signal 
    
    4th deriv: https://pmc.ncbi.nlm.nih.gov/articles/PMC9280335/pdf/fpubh-10-920946.pdf
    """
    #TODO: Currently placehold stubs

    def compute_features(self, beat: pd.DataFrame, **kwargs) - > dict:
        features = {
            'q1': self._compute_q1(beat),
            'q2': self._compute_q2(beat),
            'q3': self._compute_q3(beat),
            'q4': self._compute_q4(beat),
        }

    def _compute_q1(self, beat: pd.DataFrame):
        """
        q1 - Early systolic component 
        """
        return None

    def _compute_q2(self, beat: pd.DataFrame):
        """
        q2 - Middle systolic component
        """
        return None

    def _compute_q3(self, beat: pd.DataFrame):
        """
        q3 - Middle systolic Component
        """
        return None

    def _compute_q4(self, beat: pd.DataFrame):
        """
        q4 - End diastolic component
        """
        return None


class PulseWaveFeatures:
    """
    Orchestrator for extracting pulse wave features from PPG signals
        
        1. Sort data
        2. Applies signal smoothing - smooth functions 
        3. Computes derivatives
        4. Extracts beat-level features using modular extractors
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.f_extractor_y = FeatureExtractorY()
        self.f_extractor_dydx = FeatureExtractorDydx()
        self.f_extractor_d2ydx2 = FeatureExtractorD2ydx2()
        self.f_extractor_d3ydx3 = FeatureExtractorD3ydx3()
        self.f_extractor_d4ydx4 = FeatureExtractorD4ydx4()

    
    def compute(Self) -> (pd.DataFrame, pd.DataFrame):
        """
        Run complete pipeline for extracting all pulse wave features

        Return:
            tuple: (df with processed signals, beat-level features)
        """
        self._sort_data()
        self._apply_signal_smoothing()
        self._compute_derivatives()
        beat_features = self._extract_beat_features()
        
        return self.data, beat_features


    def _sort_data(self):
        self.data.sort_values(by=['global_beat_index', 'timestamp_ms']i, inplace=True)


    def _apply_signal_smoothing(self):
        """
        Smooth the signal for each beat using chosen method:
            - fda_bspline
            - rolling_avg
            - savitszky-golay
        
        Returns:
            Modifies the self.data df in place by adding the output column.

        """
        from .signal_smoothing import SignalSmoothing
        smoother = SignalSmoothing(
            data=self.data,
            signal_col='filtered_value',
            group_col='global_beat_index',
            output_col='sig_smooth'
        )
        
        smoother.group_apply(method="fda_bspline", n_basis=21, order=4)


    def _compute_derivatives(self):
        """
        Compute the 1st, 2nd, & 3rd derivatives of the smoothed signal
        
        Returns:
            Nothing, the columns are added inplace of the parent class self.data df
        """ 
        from .derivatives_calculator import DerivativesCalculator
        calculator = DerivativesCalculator(
            data = self.data,
            time_col='timestamp_ms',
            signal_col='sig_smooth',
            group_col='global_beat_index'
        )

        calculator.compute_first_derivative()
        calculator.compute_second_derivative()
        calculator.compute_third_derivative()


    def _extract_beat_features(self) -> pd.DataFrame:
        """
        Computes beat-level features and returns them in a new DataFrame

        Returns:
            pd.DataFrame: Each row is a beat_id, columns are feature dictionaries or features
        """
 
        features_list = []

        for beat_idx, beat in self.data.groupby('global_beat_index'):
            #TODO: Need to check this is actually the global beat index
            beat_features = {'global_beat_index': beat_idx}

            features_y = self.f_extractor_y.compute_features(beat)
            beat_features.update(features_y) 

            features_dydx = self.f_extractor_dydx.compute_features(beat)
            beat_features.update(features_dydx)

            features_d2ydx2 = self.f_extractor_d2ydx2.compute_features(beat)
            beat_features.update(features_d2ydx2)

            features_d3ydx3 = self.f_extractor_d3ydx3.compute_features(beat)
            beat_features.update(features_d3ydx3)

            features_d4ydx4 = self.f_extractor_d4ydx4.compute_features(beat)
            beat_features.update(features_d4ydx4)

            features_list.appened(beat_features)

        return pd.DataFrame(features_list)
            
  
