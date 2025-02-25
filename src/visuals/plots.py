import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

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

    def sensor_vs_time(device: str, subject: str, condition: str, sensor:str, column_name:str):
        # Using data_model format
        # Plots PPG vs timestamp_ms
        plt.plot(data[subject][condition][sensor]["timestamps_ms"], data[subject][condition][sensor][column_name])
        plt.title(f"{device} {sensor} vs time")
        plt.show()

    def sensor_vs_time2(subject, data):
        plt.plot(data['filtered_value'], data['timestamp_ms'], linewidth=10)
        plt.title(f"PPG Intensity vs Time - Subject: {subject}")
        plt.xlabel("Time (ms)")
        plt.ylabel("PPG Intensity (A.U.)")
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
            print(f"No features found for global_beat_index {global_beat_index}.")
            return

        # Extract key features
        def extract_feature(features, outer_key, inner_key, default=None):
            """
            Safely extracts a nested feature from a DataFrame column.

            Args:
                features (pd.DataFrame): DataFrame containing the feature dictionaries.
                outer_key (str): The key for the outer dictionary (e.g., 'y', 'dydx').
                inner_key (str): The key within the nested dictionary to extract (e.g., 'systole').
                default: Value to return if the key does not exist (default is None).

            Returns:
                The value corresponding to the nested key, or the default if not found.
            """
            if outer_key not in features.columns:
                raise KeyError(f"Outer key '{outer_key}' not found in DataFrame columns.")

            value = features[outer_key].values[0]
            if not isinstance(value, dict):
                raise TypeError(f"Expected a dictionary for column '{outer_key}', "
                                f"but got {type(value).__name__}.")
            
            return value.get(inner_key, default)
        
        # unpack features 
        y_systole_idx = extract_feature(features,'y', 'systole')['idx_local']
        y_systole_time = extract_feature(features,'y', 'systole')['time']
        y_diastole_idx = None

        dydx_ms_idx = extract_feature(features, 'dydx', 'ms')
        
        if extract_feature(features, 'dydx', 'systole')['detected']:
            dydx_systole_idx = extract_feature(features,'dydx', 'systole')['idx_local']
        else:
            dydx_systole_idx=0

        if extract_feature(features, 'dydx', 'diastole')['detected']:
            dydx_diastole_idx = extract_feature(features,'dydx', 'diastole')['idx_local']
        else:
            dydx_diastole_idx = 0

        a_wave_idx = extract_feature(features, 'd2ydx2', 'a_wave')['idx_local']
        b_wave_idx = extract_feature(features, 'd2ydx2', 'b_wave')['idx_local']
        c_wave_idx = extract_feature(features, 'd2ydx2', 'c_wave')['idx_local']
        d_wave_idx = extract_feature(features, 'd2ydx2', 'd_wave')['idx_local']
        e_wave_idx = extract_feature(features, 'd2ydx2', 'e_wave')['idx_local']

        # Plot the beat signal and derivatives
        fig, axs = plt.subplots(5, 1, figsize=(8, 10), sharex=True)

        # Plot original signal
        # Center original signal around the mean for comparison with bspline 
        axs[0].plot(beat_data['timestamp_ms'], beat_data['ppg'], label='PPG Signal', linewidth=1.5)
        axs[0].set_title("PPG Original")
        axs[0].set_ylabel("Amplitude")
        axs[0].grid(True)
        axs[0].legend()

        # Plot filtered signal
        axs[1].plot(beat_data['timestamp_ms'],
                    beat_data["filtered_value"],
                    label="PPG - Chebyvshev filter",
                    linewidth=1.5)

        axs[1].plot(beat_data['timestamp_ms'],
                    beat_data["sig_smooth"],
                    label="PPG Smoothed",
                    linewidth=1.5)

        if y_systole_idx is not None and y_systole_idx < len(beat_data):
            axs[1].scatter(beat_data.iloc[y_systole_idx]['timestamp_ms'], 
                           beat_data.iloc[y_systole_idx]['filtered_value'], 
                           color='red', label='Systole (y)', zorder=5)
        else:
            print(f"issue with y_systole_idx = {y_systole_idx}")
        if y_diastole_idx is not None and y_diastole_idx < len(beat_data):
            axs[1].scatter(beat_data.iloc[y_diastole_idx]['timestamp_ms'], 
                           beat_data.iloc[y_diastole_idx]['filtered_value'], 
                           color='blue', label='Diastole (y)', zorder=5)
 
        axs[1].set_title("PPG after Chebyshev Filter and Smoothing")
        
        # Plot first derivative
        axs[2].plot(beat_data['timestamp_ms'], beat_data['sig_1deriv'], label='1st Derivative', linewidth=1.5)
        axs[2].set_title("1st Derivative")
        axs[2].set_ylabel("Amplitude")
        axs[2].grid(True)
        
        # Annotate fiducials for first derivative
        if dydx_ms_idx is not None and dydx_ms_idx < len(beat_data):
            axs[2].scatter(beat_data.iloc[dydx_ms_idx]['timestamp_ms'],
                           beat_data.iloc[dydx_ms_idx]['sig_1deriv'],
                           color="orange", label='ms (dydx)', zorder=5)
        else:
            print(f"ms value invalid: {dydx_ms_idx}")

        if dydx_systole_idx is not None and dydx_systole_idx < len(beat_data):
            axs[2].scatter(beat_data.iloc[dydx_systole_idx]['timestamp_ms'], 
                           beat_data.iloc[dydx_systole_idx]['sig_1deriv'], 
                           color='red', label='Systole (dydx)', zorder=5)
        
        if dydx_diastole_idx is not None and dydx_diastole_idx < len(beat_data):
            axs[2].scatter(beat_data.iloc[dydx_diastole_idx]['timestamp_ms'], 
                           beat_data.iloc[dydx_diastole_idx]['sig_1deriv'], 
                           color='blue', label='Diastole (dydx)', zorder=5)
 
        # Plot second derivative
        axs[3].plot(beat_data['timestamp_ms'], beat_data['sig_2deriv'], label='2nd Derivative', linewidth=1.5)
        axs[3].set_title("2nd Derivative")
        axs[3].set_ylabel("Amplitude")
        axs[3].grid(True)

        # Annotate fiducials for second derivative
        for wave_idx, label, color in zip([a_wave_idx, b_wave_idx, c_wave_idx, d_wave_idx, e_wave_idx], ['a','b','c','d','e'], ['red','purple','orange','green','purple']):
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

        for ax in axs:
            ax.legend()
        fig.suptitle(f"Beat: {global_beat_index}")
        plt.tight_layout()
        plt.show()

    def app(sections, subject):
        plt.rcParams.update({
            "font.size": 12,           # Base font size
            "font.weight": "bold",     # Bold fonts
            "axes.labelsize": 14,      # Axis label font size
            "axes.labelweight": "bold",
            "axes.linewidth": 1.5,     # Thicker axis lines
            "xtick.labelsize": 12,     # X tick label font size
            "ytick.labelsize": 12,
            "figure.dpi": 150,         # Increase figure DPI for better clarity
        })
        x = sections[0]['timestamp_ms']
        y = sections[0]['filtered_value']

        fig, ax = plt.subplots(figsize=(7, 5))  # A smaller figure size

        # Plot the data
        ax.plot(x, y, color='red', linewidth=2)

        # Keep the y-axis label but remove its tick marks and labels:
        ax.set_ylabel("PPG Intensity (A.u.)")            # Keep the label
        ax.set_yticks([])                     # Remove the y-axis ticks
        ax.tick_params(axis='y', which='both', direction="in",
                       length=0, labelleft=False)  # Hide tick lines and labels

        # Limit the number of x-axis ticks for a cleaner look
        # One way is to specify the tick positions manually:
        #ax.set_xticks([0, 5, 10])
        # Alternatively, you can use a locator:
        # from matplotlib.ticker import MaxNLocator
        # ax.xaxis.set_major_locator(MaxNLocator(nbins=3))

        ax.set_xlabel("Time (ms)")
        
        ax.tick_params(
            axis='x',
            which='both',
            direction='in',  # Ticks go into the plot
            length=5,        # Tick length (adjust as needed)
            width=1.5,       # Tick width
            bottom=True,     # Draw ticks at bottom
            top=True        # We are hiding the top spine, so no top ticks
        )
        # Make the top and right spines invisible (common in scientific publications)
        #ax.spines['top'].set_visible(False)
        #ax.spines['right'].set_visible(False)

        # For consistency, you could also hide the bottom or left spines if desired:
        # ax.spines['bottom'].set_linewidth(1.5)
        # ax.spines['left'].set_linewidth(1.5)

        # Adjust subplot layout to reduce extra whitespace
        #plt.tight_layout()
        ax.set_title(f"PPG - 5 Pulses - Subject {subject}", fontweight='bold')

        plt.show()


    def plot_five_offset_signals(subjects):
        """
        Assumes:
          - subjects is a list of at least 5 Subject objects
          - each subject has a single condition named 'cond'
          - each condition has a 'ppg' SensorData object
          - that SensorData has a 'processed_data' DataFrame with 'timestamp_ms' and 'filtered_value'
        """

        # Configure some style defaults
        plt.rcParams.update({
            "font.size": 12,
            "font.weight": "bold",
            "axes.labelsize": 14,
            "axes.labelweight": "bold",
            "axes.linewidth": 1.5,
            "figure.dpi": 150,
        })

        fig, ax = plt.subplots(figsize=(7, 5))

        # Decide on colors and a consistent vertical offset
        colors = ["red", "blue", "green", "orange", "purple"]
        vertical_offset = 2000  # Adjust as needed for clarity
        
        for i in range(5):
            subj = subjects[i]
            
            # Extract your x/y data
            sensor_df = subj.conditions['cond'].sensors['ppg'].processed_data
            x = sensor_df['timestamp_ms']
            y = sensor_df['filtered_value']
            
            # Add an offset that grows with each subject index
            offset_y = y + i * vertical_offset
            
            # Plot with a label that includes the subject ID
            ax.plot(
                x, offset_y, 
                label=f"{subj.subject_id}",   # or something else like "PPG run i"
                color=colors[i % len(colors)], 
                linewidth=2
            )

        # Label axes
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("PPG Intensity (A.u.) + offset")
        
        # Show a legend with subject IDs
        ax.legend(title="Subjects")
        
        # Optional grid & title
        ax.grid(True, which="both", linestyle="--", alpha=0.6)
        ax.set_title("PPG Signals for 5 Subjects (Offset)", fontweight="bold")

        #plt.tight_layout()
        plt.show()


    def plot_five_signals_zero_start(subjects):
        """
        Plots the first 5 subjects' PPG data so that:
          - each subject's time starts at 0 (by subtracting min timestamp).
          - each subject's signal is offset vertically to avoid overlap.
        """
        plt.rcParams.update({
            "font.size": 12,
            "font.weight": "bold",
            "axes.labelsize": 14,
            "axes.labelweight": "bold",
            "axes.linewidth": 1.5,
            "figure.dpi": 150,
        })

        fig, ax = plt.subplots(figsize=(7, 5))

        colors = ["red", "blue", "green", "orange", "purple"]
        vertical_offset = 1000  # Adjust based on your data scale

        for i in range(5):
            subj = subjects[i]
            sensor_df = subj.conditions['cond'].sensors['ppg'].processed_data

            # Force all to start at 0 by subtracting the first timestamp
            original_t = sensor_df['timestamp_ms'].to_numpy()
            x = original_t - original_t[0]

            # Optionally offset each subject's y-values
            y = sensor_df['filtered_value'].to_numpy() + i * vertical_offset

            ax.plot(
                x, y,
                label=f"{subj.subject_id}",
                color=colors[i % len(colors)],
                linewidth=2
            )

        ax.set_xlabel("Time offset (ms)")
        ax.set_ylabel("PPG Intensity (A.u.) + vertical offset")
        ax.legend(title="Subjects")

        ax.grid(True, which="both", linestyle="--", alpha=0.6)
        ax.set_title("PPG Signals (Aligned at t=0 & Offset)", fontweight="bold")

        plt.tight_layout()
        plt.show()


    def plot_signals_with_time_shift_sliders(subjects):
        """
        Plots the first 5 subjects' PPG data so you can interactively shift
        each trace in time. Each slider adjusts the time offset of one trace.
        """
        plt.rcParams.update({
            "font.size": 12,
            "font.weight": "bold",
            "axes.labelsize": 14,
            "axes.labelweight": "bold",
            "axes.linewidth": 1.5,
            "figure.dpi": 150,
        })

        # Prepare figure and adjust space at bottom for sliders
        fig, ax = plt.subplots(figsize=(8, 6))
        plt.subplots_adjust(bottom=0.3)  # Leaves room for multiple sliders

        colors = ["red", "blue", "green", "orange", "purple"]
        vertical_offset = 1000

        # We'll store the line artists, plus the original x- and y-data for each subject
        lines = []
        data_list = []  # hold (xarray, yarray) for each subject

        for i in range(5):
            subj = subjects[i]
            sensor_df = subj.conditions['cond'].sensors['ppg'].processed_data
            t_original = sensor_df['timestamp_ms'].to_numpy()
            # Start near zero
            x = t_original - t_original[0]
            y = sensor_df['filtered_value'].to_numpy() + i*vertical_offset

            (line,) = ax.plot(
                x, y, 
                color=colors[i],
                linewidth=2,
                label=f"{subj.subject_id}"
            )
            lines.append(line)
            data_list.append((x, y))

        ax.set_xlabel("Time (ms) [adjusted by slider]")
        ax.set_ylabel("PPG Intensity (A.u.) + offset")
        ax.legend()
        ax.grid(True, which="both", linestyle="--", alpha=0.6)
        ax.set_title("Interactive Time-Shift of 5 PPG Traces", fontweight="bold")

        # Create a separate slider axis for each of the 5 subjects
        # We'll stack them vertically below the main plot
        sliders = []
        slider_axes = []
        for i in range(5):
            # y-position for each new slider is (0.2 - i * slider_height)
            slider_height = 0.03
            ax_slider = plt.axes([0.15, 0.18 - i*(slider_height + 0.01), 0.7, slider_height])
            # For demonstration, allow shifting up to +/- 3000 ms
            slider = Slider(
                ax_slider, 
                f"Shift {i}", 
                valmin=-3000, 
                valmax=3000, 
                valinit=0,   # Start with no shift
                valstep=100  # Step by 100ms increments
            )
            sliders.append(slider)

        # Define an update function that re-draws the lines when a slider changes
        def update(val):
            for i, slider in enumerate(sliders):
                shift_value = slider.val
                x_original, y_original = data_list[i]
                # Just add the slider shift to the x-values
                lines[i].set_xdata(x_original + shift_value)

            fig.canvas.draw_idle()

        # Register the update function with each slider
        for s in sliders:
            s.on_changed(update)

        plt.show()
