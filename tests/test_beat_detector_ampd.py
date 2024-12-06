import numpy as np
from src.processors.beat_detector_ampd import peak_detect_ampd, compute_lms

"""
def test_peak_detect_ampd():
    # Synthetic periodic signal with noise
    t = np.linspace(0, 15, 10000)
    signal = sig_noise = 5 + np.sin(np.pi *t) + np.sin(np.pi* 2*t) + np.sin(np.pi * 0.2*t) + 0.2*t + 0.1*np.random.normal(size=len(t))

    # Detect peaks
    peaks, lms, gamma, lambda_scale = peak_detect_ampd(signal)
 
    # Verify peaks are returned
    assert len(peaks) > 0, "No peaks detected"
    
    # Validate LMS dimensions
    assert lms.shape[0] == lambda_scale + 1, "LMS dimensions do not match expected"
    assert lms.shape[1] == len(signal), "LMS does not match signal length"

    # Validate gamma len
    assert len(gamma) == lms.shape[0], "Gamma length does not match LMS rows"
    
    # Validate lambda scale range
    assert 0 <= lambda_scale < len(gamma), "Lambda scale out of range"
"""

def test_compute_lms():
    # Generate signal
    signal = np.sin(2 * np.pi * np.linspace(0, 1, 100))
    
    # Compute lms 
    lms = compute_lms(signal, implementation=1)
    
    # Validate lms dims
    expected_rows = int(np.ceil(len(signal) / 2.0)) - 1
    assert lms.shape == (expected_rows, len(signal)), "LMS dims are incorrect"

    # Validate lms values
    assert np.all((lms >= 0) & (lms <= 2)), "LMS values are out of range"
    
    # Validate local maxima
    local_maxima_indicies = [
        i for i in range(1, len(signal) - 1) if signal[i] > signal[i-1] and signal[i] > signal[i+1]]
    
    for i, idx in enumerate(local_maxima_indicies):
        assert np.any(lms[:, idx] == 0), "LMS does not mark local maxima correctly"
    
def test_empty_signal():
    signal = np.array([])
    peaks, _, _, _ = peak_detect_ampd(signal)
    assert len(peaks) == 0, "Peaks detected in empty signal"

def test_single_point_signal():
    signal = np.array([1])
    peaks, _, _, _ = peak_detect_ampd(signal)
    assert len(peaks) == 0, "Peaks detected in signal with only 1 data point"

def test_flat_line_signal():
    signal = np.ones(100)
    peaks, _, _, _ = peak_detect_ampd(signal)
    assert len(peaks) == 0, "Peaks detected in flat-line signal"

def test_linear_signal():
    signal = np.linspace(0, 10, 100)
    peaks, _, _, _ = peak_detect_ampd(signal)
    assert len(peaks) == 0, "Peaks detected in a linear non-periodic signal"
