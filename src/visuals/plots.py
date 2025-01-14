import matplotlib.pyplot as plt

class Plots:
    def __init__(self):
        pass    
    
    def ppg_series(ppg_series):
        plt.figure()
        plt.plot(ppg_series)
        plt.xlabel("Idx")
        plt.ylabel("PPG (A.U.)")
        plt.show()
    
    def ppg_series_compare(series1, series2):
        plt.figure()
        plt.scatter(x=(series1.timestamp_ms-series1.timestamp_ms.iloc[-1]),y=series1.ppg, label="series1", s=8, marker='x')
        plt.scatter(x=(series2.timestamp_ms-series2.timestamp_ms.iloc[-1]),y=series2.ppg, label="series2", s=5)
        plt.xlabel("Idx")
        plt.ylabel("PPG (A.U.)")
        plt.legend()
        plt.show()
    
    def ppg_series_compare_datetime(series1, series2):
        plt.figure()
        plt.scatter(x=series1.timestamp_ms,y=series1.ppg, label="series1", s=8, marker='x')
        plt.scatter(x=series2.timestamp_ms,y=series2.ppg, label="series2", s=5)
        plt.xlabel("Idx")
        plt.ylabel("PPG (A.U.)")
        #plt.legend()
        plt.show()
 

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

    def all_detected_troughs_and_peaks(df, value_col):
        
        plt.figure(figsize=(12, 6))
        plt.plot(df[value_col], label=value_col, alpha=0.8)
    
        troughs = df.loc[df['is_beat_trough'] == True]
        plt.scatter(troughs.index, troughs[value_col], color='blue', label='Troughs', s=25)

        peaks = df.loc[df['is_beat_peak'] == True]
        plt.scatter(peaks.index, peaks[value_col], color='red', label='Peaks', s=25)

        plt.title("Combined Sections with Detected Troughs and Peaks")
        plt.xlabel("Index")
        plt.ylabel("Filtered PPG")
        #plt.legend()
        #plt.grid(alpha=0.3)
        plt.show()
    
    def single_beat(df, beat_idx):
        plt.plot(df[beat_idx])
        plt.title(f"Beat Id: {beat_idx}")
        plt.show()
    
    def group_hr_distribution(df,bins, title_append=""):
        group_bpms = df.drop_duplicates(subset=['group_id','group_bpm'])['group_bpm']
        plt.hist(group_bpms, bins=bins, edgecolor='black', alpha=0.7)
        plt.xlabel('BPM')
        plt.ylabel('Frequency')
        plt.title(f'Distribution of HRs: {title_append}')
        plt.show()
