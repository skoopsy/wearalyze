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


    def plot_beat_with_features(data, beat_features, global_beat_index):
        """
        Plots the "beat" from the "data" dataframe and overlays the features
        from the "beat_features" dataframe.

        Parameters:
        - data: pd.DataFrame, containing the raw and processed PPG data.
        - beat_features: pd.DataFrame, containing beat-specific features.
        - global_beat_index: int, the index of the beat to plot.
        """
        # Extract the beat-specific data and features
        beat_data = data[data['global_beat_index'] == global_beat_index]
        features = beat_features[beat_features['global_beat_index'] == global_beat_index]

        if features.empty:
            raise ValueError(f"No features found for global_beat_index {global_beat_index}.")

        # Extract key features safely
        def extract_feature(features, column_name, key):
            value = features[column_name].values[0]
            if isinstance(value, dict):
                return value.get(key, None)
            raise TypeError(f"Expected a dictionary for {column_name}, but got {type(value).__name__}.")

        systole_idx = extract_feature(features, 'systole', 'idx')
        systole_time = extract_feature(features, 'systole', 'time')
        diastole_idx = extract_feature(features, 'diastole', 'idx')
        a_wave_idx = extract_feature(features, 'a_wave', 'idx')
        b_wave_idx = extract_feature(features, 'b_wave', 'idx')
        c_wave_idx = extract_feature(features, 'c_wave', 'idx')
        d_wave_idx = extract_feature(features, 'd_wave', 'idx')
        e_wave_idx = extract_feature(features, 'e_wave', 'idx')

        # Plot the beat signal
        plt.figure(figsize=(12, 6))
        plt.plot(beat_data['timestamp_ms'], beat_data['ppg'], label='PPG Signal', linewidth=1.5)

        # Highlight key points
        if systole_idx is not None and systole_idx < len(beat_data):
            plt.scatter(beat_data.iloc[systole_idx]['timestamp_ms'], 
                        beat_data.iloc[systole_idx]['ppg'], 
                        color='red', label='Systole', zorder=5)
        if diastole_idx is not None and diastole_idx < len(beat_data):
            plt.scatter(beat_data.iloc[diastole_idx]['timestamp_ms'], 
                        beat_data.iloc[diastole_idx]['ppg'], 
                        color='blue', label='Diastole', zorder=5)

        for wave_idx, label, color in zip([a_wave_idx, b_wave_idx, c_wave_idx, d_wave_idx, e_wave_idx],
                                          ['A Wave', 'B Wave', 'C Wave', 'D Wave', 'E Wave'],
                                          ['orange', 'green', 'purple', 'cyan', 'magenta']):
            if wave_idx is not None and wave_idx < len(beat_data):
                plt.scatter(beat_data.iloc[wave_idx]['timestamp_ms'], 
                            beat_data.iloc[wave_idx]['ppg'], 
                            color=color, label=label, zorder=5)

        # Add labels and legends
        plt.title(f"PPG Beat with Features (Global Beat Index: {global_beat_index})")
        plt.xlabel("Time (ms)")
        plt.ylabel("PPG Signal")
        plt.legend()
        plt.grid(True)
        plt.show()


    def plot_beat_with_features_deriv(data, beat_features, global_beat_index):
        """
        Plots the "beat" from the "data" dataframe and overlays the features
        from the "beat_features" dataframe. Includes the original signal and
        its derivatives, with fiducial points annotated on each plot.

        Parameters:
        - data: pd.DataFrame, containing the raw and processed PPG data.
        - beat_features: pd.DataFrame, containing beat-specific features.
        - global_beat_index: int, the index of the beat to plot.
        """
        # Extract the beat-specific data and features
        beat_data = data[data['global_beat_index'] == global_beat_index]
        features = beat_features[beat_features['global_beat_index'] == global_beat_index]

        if features.empty:
            raise ValueError(f"No features found for global_beat_index {global_beat_index}.")

        # Extract key features safely
        def extract_feature(features, column_name, key):
            value = features[column_name].values[0]
            if isinstance(value, dict):
                return value.get(key, None)
            #raise TypeError(f"Expected a dictionary for {column_name}, but got {type(value).__name__}.")

        systole_idx = extract_feature(features, 'systole', 'idx')
        systole_time = extract_feature(features, 'systole', 'time')
        diastole_idx = extract_feature(features, 'diastole', 'idx')
        a_wave_idx = extract_feature(features, 'a_wave', 'idx')
        b_wave_idx = extract_feature(features, 'b_wave', 'idx')
        c_wave_idx = extract_feature(features, 'c_wave', 'idx')
        d_wave_idx = extract_feature(features, 'd_wave', 'idx')
        e_wave_idx = extract_feature(features, 'e_wave', 'idx')

        # Plot the beat signal and derivatives
        fig, axs = plt.subplots(5, 1, figsize=(9, 14), sharex=True)

        # Plot original signal
        axs[0].plot(beat_data['timestamp_ms'], beat_data['ppg'], label='PPG Signal', linewidth=1.5)
        axs[0].set_title("PPG Signal")
        axs[0].set_ylabel("Amplitude")
        axs[0].grid(True)

        if systole_idx is not None and systole_idx < len(beat_data):
            axs[0].scatter(beat_data.iloc[systole_idx]['timestamp_ms'], 
                           beat_data.iloc[systole_idx]['ppg'], 
                           color='red', label='Systole', zorder=5)
        if diastole_idx is not None and diastole_idx < len(beat_data):
            axs[0].scatter(beat_data.iloc[diastole_idx]['timestamp_ms'], 
                           beat_data.iloc[diastole_idx]['ppg'], 
                           color='blue', label='Diastole', zorder=5)
        axs[0].legend()

        # Plot smoothed signal
        axs[1].plot(beat_data['timestamp_ms'], beat_data["sig_smooth"], label="PPG Rolling avg 5", linewidth=1.5)
        axs[1].set_title("PPG Smoothed")
        
        # Plot first derivative
        axs[2].plot(beat_data['timestamp_ms'], beat_data['sig_1deriv'], label='1st Derivative', linewidth=1.5)
        axs[2].set_title("1st Derivative")
        axs[2].set_ylabel("Amplitude")
        axs[2].grid(True)

        # Annotate fiducials for first derivative
        if a_wave_idx is not None and a_wave_idx < len(beat_data):
            axs[2].scatter(beat_data.iloc[a_wave_idx]['timestamp_ms'], 
                           beat_data.iloc[a_wave_idx]['sig_1deriv'], 
                           color='orange', label='A Wave', zorder=5)

        # Plot second derivative
        axs[3].plot(beat_data['timestamp_ms'], beat_data['sig_2deriv'], label='2nd Derivative', linewidth=1.5)
        axs[3].set_title("2nd Derivative")
        axs[3].set_ylabel("Amplitude")
        axs[3].grid(True)

        # Annotate fiducials for second derivative
        for wave_idx, label, color in zip([b_wave_idx, c_wave_idx], ['B Wave', 'C Wave'], ['green', 'purple']):
            if wave_idx is not None and wave_idx < len(beat_data):
                axs[3].scatter(beat_data.iloc[wave_idx]['timestamp_ms'], 
                               beat_data.iloc[wave_idx]['sig_2deriv'], 
                               color=color, label=label, zorder=5)

        # Plot third derivative
        axs[4].plot(beat_data['timestamp_ms'], beat_data['sig_3deriv'], label='3rd Derivative', linewidth=1.5)
        axs[4].set_title("3rd Derivative")
        axs[4].set_xlabel("Time (ms)")
        axs[4].set_ylabel("Amplitude")
        axs[4].grid(True)

        # Annotate fiducials for third derivative
        for wave_idx, label, color in zip([d_wave_idx, e_wave_idx], ['D Wave', 'E Wave'], ['cyan', 'magenta']):
            if wave_idx is not None and wave_idx < len(beat_data):
                axs[4].scatter(beat_data.iloc[wave_idx]['timestamp_ms'], 
                               beat_data.iloc[wave_idx]['sig_3deriv'], 
                               color=color, label=label, zorder=5)

        for ax in axs:
            ax.legend()

        plt.tight_layout()
        plt.show()
