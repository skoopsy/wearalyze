import pandas as pd

class DerivativesCalculator:
    def __init__(self, data: pd.DataFrame, time_col: str, signal_col: str, group_col: str):
        """
        Initialise

        Args:
            data: Input DataFrame
            time_col: Column name for time values
            signal_col: signal column
            group_col: group_identifier (e.g. global_beat_index)
        """

        self.data = data # Direct refere input df
        self.time_col = time_col
        self.signal_col = signal_col
        self.group_col = group_col
        self._validate_input()

    def _validate_input(self):
        """
        Validate that the columns are in the input DataFrame
        """
        missing_columns = [
            col for col in [self.time_col, self.signal_col, self.group_col] if col not in self.data.columns
        ]
        if missing_columns:
            raise ValueError(f"The following required columns are missing: {', '.join(missing_columns)}")
    
    def compute_rolling_avg(self, column):
        return self.data.groupby(self.group_col).apply(
            lambda group: group[column].rolling(window=6, center=True).mean()
        ).reset_index(level=0, drop=True)
        
    def compute_derivative(self, column: str) -> pd.Series:
        """
        Compute the derivative of a column within each group of df

        Args:
            column: col name to compute derivative of
        Returns:
            Series contraining derivative values
        """
        
        return self.data.groupby(self.group_col).apply(
            lambda group: group[column].diff() / group[self.time_col].diff()
        ).reset_index(level=0, drop=True)

    def compute_first_derivative(self):
        """
        Computes 1st derivative of a signal and stores it in a DataFrame.
        """
        #self.data["sig_avg5"] = self.compute_rolling_avg(self.signal_col)
        self.data["sig_1deriv"] = self.compute_derivative("sig_smooth")
        #self.data["sig_1deriv"] = self.compute_rolling_avg("sig_1deriv0")


    def compute_second_derivative(self):
        """
        Compute 2nd derivative of a signal and store in DataFrame
        """
        if "sig_1deriv" not in self.data:
            self.compute_first_derivative()
        self.data["sig_2deriv"] = self.compute_derivative("sig_1deriv")
        #self.data["sig_2deriv"] = self.compute_rolling_avg("sig_2deriv0")


    def compute_third_derivative(self):
        """
        Compute 3rd derivative of a signal and store in DataFrame
        """
        if "sig_2deriv" not in self.data:
            self.compute_second_derivative()
        self.data["sig_3deriv"] = self.compute_derivative("sig_2deriv")

    def get_data(self) -> pd.DataFrame:
        """
        Return df with computed derivatives
        """
        return self.data
    


