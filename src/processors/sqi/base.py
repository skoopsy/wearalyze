from abc import ABC, abstractmethod

class SQIBase(ABC):
    @abstractmethod
    def compute(self, segment):
        """ Compute SQI for input segment """
        pass
