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
