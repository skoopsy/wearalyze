import pandas as pd

class SignalSmoothing:
    """
    Smooth signals in a pd.DataFrame via smoothing or functional data 
    analysis.
    """
    def __init__(self, data: pd.DataFrame, signal_col: str, group_col: str):
        self.data = data
        self.signal_col = signal_col
        self.group_col = group_col

    def savitzky_golay(y: pd.Series ):
        """
        Use savgol smoothing on signal
        """
        from scipy.signal import savgol_filter
        window_size = 21
        poly_order = 3
        y_smooth = savgol_filter(y, window_size, poly_order)
 
        return y_smooth

    def fda_bspline():
        """
        use scikit-fda package to fit a b-spline to the waveforms for numerical differentiation
        doi:10.1007/b98888.
        https://fda.readthedocs.io/en/stable/index.html 
        """
        
        pass
  
    def rolling_avg(self):
        """
        """
        return self.data.groupby(self.group_col).apply(
            lambda group: group[self.signal_col].rolling(window=6, center=True).mean()
        ).reset_index(level=0, drop=True)
 
