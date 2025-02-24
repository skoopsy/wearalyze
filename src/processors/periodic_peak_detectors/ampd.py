from src.processors.periodic_peak_detectors.base import BaseDetector

import numpy as np
from scipy.signal import detrend
import sys # For debugging memory usage

class AMPDDetector(BaseDetector):
    def detect(self, signal, **kwargs):
        peaks, lms, gamma, lambda_scale = self._peak_detect_ampd(signal)
        
        return {"peaks":peaks, "lms":lms, "gamma":gamma, "lambda_scale":lambda_scale}

    def _peak_detect_ampd(self, signal):
        """
        Automatic Multiscale Peak Detection for noisey periodic and 
        quasia-periodic signalsdoi:10.3390/a5040588

        I have added some more robustness with edge case handling such as small
        or linear signals    
        
        Note: This uses a lot of memory, I can't recall where the part is that
        limits the input size    
        
        Args:
            signal - 1D signal to run ampd on (numpy.ndarray)

        Returns:
            peaks - Indices of detected peaks (numpy.ndarray)
            lms - Local Maxima Scalogram matrix (numpy.ndarray)
            gamma - Vector used to find global minimum (numpy.ndarray)
            lambda_scale - Scale at which global minimum occurs (int)
        """
        print("[AMPD] Starting ampd _peak_detect_ampd") 
        # Handle small input signals:
        if signal.size < 3:
            return np.array([]), np.array([]), np.array([]), 0
            print("[AMPD] Rejected small signal (<3)")    
        # AMPD algo
        detrended_signal = detrend(signal) # least mean square linear fit
        print("[AMPD] Signal detrending successful")
        lms = self._compute_lms(detrended_signal) # Local Maxima Scalogram
        print("[AMPD] Compute LMS successful")
        gamma = np.sum(lms, axis=1) # Row wise summation - sum of scalogram per scale
        lambda_scale = np.argmin(gamma) # Scale with lowest sum - most maximas (0 vals)
        lms = lms[:lambda_scale + 1, :] # Remove scales greater than lambda from lms
        sigma = np.std(lms, axis=0) # Column-wise std deviation - continuity between scales
        peaks = np.where(sigma == 0)[0] # Select where std dev is zero! maximas are 0s - smort)

        # Handle linear signal
        #if lambda_scale == 0 or np.all(gamma > 0):
        #    return np.array([]), lms, gamma, lambda_scale
        return peaks, lms, gamma, lambda_scale


    def _compute_lms(self, signal, implementation=1):
        """
        Compute the local maxima scaleogram of a 1D signal (numpy.ndarray).

        Becareful this implementation gives random values to the lms unless maxima
        which is set to 0. A heatmap of the lms might look interesting but it needs
        to be made binary which are zero and non-zero values. The zero will
        correspond to maxima.
        """
        print("[AMPD] _compute_lms started...")
        N = len(signal) # Length of signal
        L = int(np.ceil(N / 2.0)) - 1 # Maximum window size
        # Initialise local maxima scalogram (LMS)
        lms = np.random.rand(L, N) + 1 # Rand val in [1, 2)
        self._memory_usage(lms)
        match implementation:
            case 0: # Pure python Loop version
                for k in range(1, L + 1):
                    for i in range(k, N - k): # Avoid edge issues
                        if signal[i] > signal[i - k] and signal[i] > signal[i + k]:
                            lms[k - 1, i] = 1

            case 1: # Vectorised using Numpy
                print("[AMPD] starting vectorised lms compute")
                for k in range(1, L + 1):
                    idx = np.arange(k, N - k)
                    condition = (signal[idx] > signal[idx - k]) & (signal[idx] > signal[idx + k])
                    # If condition is true at Idx, set lms corresponding value to 0 - a local maxima
                    lms[k - 1, idx[condition]] = 0

        return lms
    
    def _memory_usage(self, var):
        print(f"[AMPD] Memory usage of variable: {sys.getsizeof(var)} bytes")
