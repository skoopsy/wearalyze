import numpy as np
from src.processors.beat_detectors.ampd import AMPDDetector

"""
def test_peak_detect_ampd():
    # Initialize the detector
    detector = AMPDDetector()
    
    # Synthetic periodic signal with noise
    t = np.linspace(0, 15, 10000)
    signal = 5 + np.sin(np.pi * t) + np.sin(2 * np.pi * t) + np.sin(0.2 * np.pi * t) + 0.2 * t + 0.1 * np.random.normal(size=len(t))

    # Detect peaks
    results = detector.detect(signal)
    peaks, lms, gamma, lambda_scale = results["peaks"], results["lms"], results["gamma"], results["lambda_scale"]

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
    # Initialize the detector
    detector = AMPDDetector()
    
    # Generate signal
    signal = np.sin(2 * np.pi * np.linspace(0, 1, 100))

    # Compute LMS
    lms = detector._compute_lms(signal, implementation=1)

    # Validate LMS dimensions
    expected_rows = int(np.ceil(len(signal) / 2.0)) - 1
    assert lms.shape == (expected_rows, len(signal)), "LMS dimensions are incorrect"

    # Validate LMS values
    assert np.all((lms >= 0) & (lms <= 2)), "LMS values are out of range"

def test_empty_signal():
    # Initialize the detector
    detector = AMPDDetector()
    signal = np.array([])
    results = detector.detect(signal)
    assert len(results["peaks"]) == 0, "Peaks detected in empty signal"

def test_single_point_signal():
    # Initialize the detector
    detector = AMPDDetector()
    signal = np.array([1])
    results = detector.detect(signal)
    assert len(results["peaks"]) == 0, "Peaks detected in signal with only 1 data point"

def test_flat_line_signal():
    # Initialize the detector
    detector = AMPDDetector()
    signal = np.ones(100)
    results = detector.detect(signal)
    assert len(results["peaks"]) == 0, "Peaks detected in flat-line signal"
"""
def test_linear_signal():
    # Initialize the detector
    detector = AMPDDetector()
    signal = np.linspace(0, 10, 100)
    results = detector.detect(signal)
    assert len(results["peaks"]) == 0, "Peaks detected in a linear non-periodic signal"
"""
