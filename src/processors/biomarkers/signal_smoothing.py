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

    def _fda_bspline(self, series: pd.Series, n_basis: int = 10, order: int = 3) -> pd.Series:
        """
        Fit a B-spline basis to the input Pandas Series using scikit-fda
        and return the smoothed values. The index of the series is taken
        as the 'x' domain. This allows for subsequent numerical 
        differentiation on a smooth functional representation.
        """
        import numpy as np
        import skfda
        from skfda.representation.basis import BSplineBasis
        from skfda.preprocessing.smoothing import BasisSmoother
        
        # Convert index and values to numpy arrays
        x = np.array(series.index, dtype=float)
        y = np.array(series, dtype=float)
        
        # Handle cases where the series might be too short
        if len(series) < n_basis:
            raise ValueError("Number of basis functions exceeds series length. "
                             "Try reducing 'n_basis' or using a longer series.")
        
        # Define the domain range for the B-spline
        domain_range = (x.min(), x.max())
        
        # Define the B-spline basis
        basis = BSplineBasis(n_basis=n_basis, domain_range=domain_range)
        
        # Create functional data from the raw y-values
        fd = skfda.FDataGrid(data_matrix=y.reshape(1, -1), grid_points=x)
        
        # Create a smoother using the basis
        smoother = BasisSmoother(basis=basis)
        
        # Fit and transform the data to get functional representation
        fd_smooth = smoother.fit_transform(fd)
        
        # Evaluate (sample) the smoothed function at the original x points
        y_smooth = fd_smooth.evaluate(x).ravel()
        
        # Return as a Pandas Series with the same index as the original
        return pd.Series(y_smooth, index=series.index)

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
                flagged_groups.append((group[self.group_col].iloc[0], str(e)))
                return pd.Series([pd.NA] * len(group), index=group.index)

        # Apply smoothing method and store results in a new column
        smoothed_results = self.data.groupby(self.group_col).apply(
            lambda group: apply_method(group)
        ).reset_index(level=0, drop=True)

        self.data[f"sig_smooth"] = smoothed_results

        if flagged_groups:
            for group, error in flagged_groups:
                print(f"Warning: Group '{group}' could not be processed due to error: {error}")
