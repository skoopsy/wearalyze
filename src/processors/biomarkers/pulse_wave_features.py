class PulseWaveFeatures:
    def __init__(self, data):
        self.data = data.copy()
    
    def compute(self):
        
        # Sort data, probably unnessicary
        self.data = self.data.sort_values(by=['group_id','timestamp'])    
    
        # Compute derivatives
        self.first_derivative()
        self.second_derivative()
        self.third_derivative()

        # Extract features
        self.features_first_derivative()
        self.features_second_derivative()
        self.features_third_derivative()
        self.features_y()

        return self.data

    def first_derivative(self):
        self.data['first_derivative'] = (
            self.data.groupby('group_id')['filtered_value'].diff() 
        )

    def second_derivative(self):
        self.data['second_derivative'] = (
            self.data.groupby('group_id')['first_derivative'].diff() 
        )
    
    def third_derivative(self):
        self.data['third_derivative'] = (
            self.data.groupby('group_id')['second_derivative'].diff() 
        )

    def features_first_derivative(self):

        # Create boolian column to mark zero_crossing points
        data.groupby('group_id')['first_derivative'].apply(process_beat_zero_crossings)
        
        zero_crossing_rows = data[data['1stderiv_zero_crossing']]        
        
        # Systole - first zero crossing point
        # Should be after the first peak
        systole_peak = 0       

        # Diastole Peak - Third zero crossing point
        # Shold be after the second peak
        diastole_peak = 0
        pass

    def features_second_derivative(self):
        pass

    def features_third_derivative(self):
        pass

    def features_y(self):
        pass

    def find_zero_crossings(signal: pd.Series, crossing_type: str):
        """
        Returns the index of where a signal crosses zero in a specified 
        direction (from negative to positive, positive to negative, or both). 
        
        The returned index will be the data point before or at the zero
        point as opposed to the data point after the zero-crossing.

        Args:
            signal (pd.Series)
            crossing_type (str): Specify zero crossing direction: pos2neg
                                                                  neg2pos
                                                                  both
        
        Returns:
            zero_crossings (list(list)): List of zero crossing points with 
                                         index, value
        """    

        zero_crossings = []

        # Convert dtype explicitly as > does it implicitly
        signal = np.array(signal)

        pos = signal > 0
        npos = ~pos
        
        if crossing_type == "pos2neg":
            zero_crossings = ((pos[:-1] & npos[1:])).nonzero()[0]
        if crossing_type == "neg2pos":
            zero_crossings = (pos[:-1] & npos[1:]) 
        if crossing_type == "both":
            zero_crossings = ((pos[:-1] & npos[1:]) | (npos[:-1] & pos[1:])).nonzero()[0]
        elif:
            raise ValueError("Inalid crossing_type: {crossing_type}  .Please use pos2neg, neg2pos, or both")

        zero_crossings = zero_crossings.tolist() # Convert back to list

        return zero_crossings

    def process_beat_zero_crossings(beat):
        """
        Computes the zero crossing points of the signal and marks them in a 
        boolean column of a df
        """        

        zero_crossings = find_zero_crossings(beat['first_derivative'].values)
        beat['1stderiv_zero_crossing'] = False
        beat.loc[beat.index[zero_crossings], '1stderiv_zero_crossing'] = True
        
        return beat
        
