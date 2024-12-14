from src.processors.sqi.base import SQIBase

class CompositeSQI(SQIBase):
    def __init__(self, sqi_list, combine_strategy="sequential_validation"):
        """
        Initialise CompositeSQI with a list of SQIs and a strategy for
        combining them
        
        args:
            sqi_list (list[SQI]): List of SQI instances
            combine_strategy (str): How to combine the results
        """
        self.sqi_list = sqi_list
        self.combine_strategy = combine_strategy

    def compute(self, segment):
        """
        Compute the composite SQI for a given segment

        args:
            segment (pd.DataFrame or pd.Series): The segment to perform SQI on
        
        returns:
            float: The combined SQI value. - maybe bool?
        """

        sqi_results = [sqi.compute(segment) for sqi in self.sqi_list]

        if self.combine_strategy == "average":
            return sum(sqi_results) / len(sqi_results)
        #TODO Revisit the output of this when api better understood
        elif self.combine_strategy == "sequential_validation":
            pass
        else:
            raise ValueError(f"Unknown combination strategy: {self.combine_strategy}")
