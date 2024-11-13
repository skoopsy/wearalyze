import numpy as np

def beat_detect_msptd(data, max_interval=None):
	"""
	Detect peaks and troughs in a (quasi-)periodic signal using:
		- Modified Scholkmann Algorithm
		- Multi-Scale Peak and Trough Detection
		- doi: 

	Args:
		data (numpy.ndarray): Input signal
		max_interval (int, optional): Max scale to consider for local maxima scaleogram. Defaults to half the signal length
		
	Returns:
		numpy.ndarray: Indicies of detected peaks
		numpy.ndarray: Indicies of detected troughts
		numpy.ndarray: Local maxima scalogram
		numpy.ndarray: Local minima scalogram
	"""
	
	# Input signal length
	N = len(data)

	# Set length for scaleogram
	if max_interval is None:
		L = int(np.ceil(N / 2)) - 1
	else:
		L = int(np.ceil(max_interval / 2)) - 1
	
	# Detrend data by subtracting the mean
	mean_val = np.nanmean(data)
	data[np.isnan(data)] = mean_val
	data = data - np.mean(data)
	
	# Initialise local max and min scaleograms
	Mx = np.zeros((N, L), dtype=bool)
	Mn = np.zeros((N, L), dtype=bool)

	# Compute local maxima scalogram	
	for scale in range(L):
		k = scale + 1
		for i in range(k + 1, N - k + 1):
			# Check if current value is a local maxima
			if data[i-1] > data[i - k - 1] and data[i-1] > data[i + k - 1]:
				Mx[i - 1, scale] = True
			# Check if current value is a local minima
			if data[i-1] < data[i - k - 1] and data[i-1] < data[i + k - 1]:	
				Mn[i - 1, scale] = True
	
	maxima_scalogram = Mx
	minima_scalogram = Mn

	# Find scale with the most maxima and minima
	# Sums boolean vals in each column of Mx and Mn
	# Col with the most zeros (true values) corresponds to scale with most max and minima
	Y = np.sum(Mx, axis=0)
	d_max = np.argmax(Y)
	Mx = Mx[:, :d_max + 1]

	Y = np.sum(Mn, axis=0)
	d_min = np.argmax(Y)
	Mn = Mn[:, :d_min + 1]

	# Find position of peaks and troughs
	# Sum non-zero values in each row of Mx and Mn
	# Rows with a sum of 0 correspond to the position of a peak and trough
	Zx = np.sum(~Mx, axis=1)
	Zn = np.sum(~Mn, axis=1)
	peaks = np.where(Zx == 0)[0]
	troughs = np.where(Zn == 0)[0]

	return peaks, troughs, maxima_scalogram, minima_scalogram
