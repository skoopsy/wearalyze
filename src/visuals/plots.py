import matplotlib.pyplot as plt

def plot_ppg_sections_vs_time(sections):
	"""Plot original and filtered sections of PPG data."""

	for i, section in enumerate(sections):
		plt.figure()
		elapsed_time = (section['timestamp'] - section['timestamp'].iloc[0]).dt.total_seconds()
		plt.plot(section['timestamp'], section['value'], label="Original")
		plt.plot(section['timestamp'], section['filtered_value'], label="Filtered")
		plt.xlabel('Time')
		plt.ylabel('PPG Value')
		plt.title(f'Section {i+1}')
		plt.legend()
		plt.show()

def plot_detected_inflections(data, peaks, troughs):
    """
    Plot the original signal with detected peaks and troughs

    Args:
        data (numpy.ndarray): The original input signal
        peaks (numpy.ndarray): Indices of detected peaks
        troughs (numpy.ndarray): Indicies of detected troughs
    """

    plt.figure(figsize=(12,6))
    plt.plot(data['filtered_value'], label='Signal')

    # Plot peaks in red
    plt.scatter(peaks, data['filtered_value'][peaks], color='red', label='Peaks', marker='^')

    # Plot troughs in blue
    plt.scatter(troughs, data['filtered_value'][troughs], color='blue', label='Troughs', marker='v')

    plt.title('Detected Peaks and Troughs')
    plt.xlabel('Index')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_scaleogram(scaleogram, title='Scaleogram'):
    """
    Plot the scaleogram (local maxima or minima matrix)

    Args:
        scaleogram (numpy.ndarray): The local maxima or minima scaleogram
        title (str, optional): Title for the plot
    """

    plt.figure(figsize=(12,6))
    plt.imshow(scaleogram.T, aspect='auto', cmap='binary', origin='lower')
    plt.title(title)
    plt.xlabel('Index')
    plt.ylabel('Scale')
    plt.colorbar(label='Local Max/Min')
    plt.show()

def plot_lms(lms):
    return None

def plot_signal_detected_peaks(signal, peaks, beat_detector):
    plt.figure(figsize=(14, 6))
    plt.plot(signal, label='Original Signal Section')
    plt.plot(signal.iloc[peaks], 'ro', label='Detected Peaks')
    plt.title(f'Raw Signal with Detected Peaks ({beat_detector})')
    plt.xlabel('Index')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid(True)
    plt.show()

