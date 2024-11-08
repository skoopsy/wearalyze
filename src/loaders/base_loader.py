from abc import ABC, abstractmethod
import pandas as pd

class BaseLoader(ABC):
	@abstractmethod
	def load_data(self, file_paths):
		"""Load and pre-process data from input files"""
		pass
