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
            self.data.groupby('group_id')['filtered_value'].diff() /
            self.data.groupby('group_id')['timestamp_ms'].diff()
        )

    def second_derivative(self):
        self.data['second_derivative'] = (
            self.data.groupby('group_id')['first_derivative'].diff() /
            self.data.groupby('group_id')['timestamp_ms'].diff()
        )
    
    def third_derivative(self):
        self.data['third_derivative'] = (
            self.data.groupby('group_id')['second_derivative'].diff() /
            self.data.groupby('group_id')['timestamp_ms'].diff()
        )

    def features_first_derivative(self):
        
        pass

    def features_second_derivative(self):
        pass

    def features_third_derivative(self):
        pass

    def features_y(self):
        :pass
