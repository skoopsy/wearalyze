import pandas as pd

class SignalSmoothing:
    """
    Smooth signals in a pd.DataFrame via smoothing or functional data 
    analysis.
    """
    def __init__(self, 
                data: pd.DataFrame, 
                signal_col: str, 
                group_col: str,
                output_col: str
        ):
        self.data = data
        self.signal_col = signal_col
        self.group_col = group_col
        self.output_col = output_col

    def _rolling_avg(self, series: pd.Series, window: int = 5) -> pd.Series:
        """
        Calculate rolling average on a series
        """
        return series.rolling(window=window, center=True).mean()

    def _savitzky_golay(self, 
                        series: pd.Series, 
                        window_size: int = 13,
                        poly_order: int = 3
        ) -> pd.Series:
        """
        Apply Savitzky-Golay filter to a series
        """    
        
        from scipy.signal import savgol_filter
        if len(series) < window_size:
            raise ValueError("Window size is greater than series length")
        return pd.Series(savgol_filter(series, window_size, poly_order), index=series.index)

    def _fda_bspline(self, series: pd.Series, n_basis: int = 10):
        """
        Fit a B-spline to data using scikit-fda
        """
        pass



  
    def group_apply(self, method: str, **kwargs):
        """
        Apply a specified smoothing method by group and update the original DataFrame with the smoothed values.
        """
        if not hasattr(self, f"_{method}"):
            raise ValueError(f"Method '{method}' is not implemented.")

        method_func = getattr(self, f"_{method}")

        flagged_groups = []

        def apply_method(group):
            try:
                result = method_func(group[self.signal_col], **kwargs)
                return result
            except ValueError as e:
                flagged_groups.append(group[self.group_col].iloc[0])
                return pd.Series([pd.NA] * len(group), index=group.index)

        # Apply smoothing method and store results in a new column
        smoothed_results = self.data.groupby(self.group_col).apply(
            lambda group: apply_method(group)
        ).reset_index(level=0, drop=True)

        self.data[self.output_col] = smoothed_results

        if flagged_groups:
            print(f"Warning: The following groups could not be processed due to errors: {flagged_groups}")
    
    
    def savitzky_golay(self):
        """
        Use savgol smoothing on signal
        """
        window_size = 21
        poly_order = 3
        y_smooth = savgol_filter(y, window_size, poly_order)
 
        return y_smooth

    def fda_bspline(self):
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
 
