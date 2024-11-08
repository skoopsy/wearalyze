from scipy.signal import cheby2, filtfilt
import pandas as pd
import numpy as np
from datetime import timedelta

class PPGPreProcessor:
	def __init__(self, data, config):
		self.data = data
		self.config = config

	def create_thresholded_sections(self):
		"""Identify valid sections of data based on threshold."""
		self.data['timestamp'] = pd.to_datetime(self.data['timestamp'], unit='ms')
		threshold = self.config['ppg_preprocessing']['threshold']
		min_duration = self.config['ppg_preprocessing']['min_duration']
		
		# Mark sections above threshold
		self.data['above_threshold'] = self.data['value'] > threshold
		self.data['section_id'] = (self.data['above_threshold'] != self.data['above_threshold'].shift()).cumsum()
		sections = [section_df for _, section_df in self.data[self.data['above_threshold']].groupby('section_id')]

		# Filter sections by duration
		valid_sections = []
		for section in sections:
			start_time = section['timestamp'].iloc[0]
			end_time = section['timestamp'].iloc[-1]
			duration = end_time - start_time

			if duration >= timedelta(seconds=min_duration):
				section['data_points'] = len(section)
				valid_sections.append(section)
		return valid_sections

	def filter_cheby2(self, sections):
		"""Apply Chebyshev Type II filter to each section."""
		sample_rate = self.config['filter']['sample_rate']
		lowcut = self.config['filter']['lowcut']
		highcut = self.config['filter']['highcut']
		order = self.config['filter']['order']
		nyquist = 0.5 * sample_rate

		b, a = cheby2(order, 20, [lowcut / nyquist, highcut / nyquist], btype='band')
		filtered_sections = []
	
		for section in sections:
			filtered_values = filtfilt(b, a, section['value'])
			section['filtered_value'] = filtered_values
			filtered_sections.append(section)
		
		return filtered_sections
