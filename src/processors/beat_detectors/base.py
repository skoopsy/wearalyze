from abc import ABC, abstractmethod

class BaseDetector(ABC):
    """ Abstract base class for beat detectors"""

    @abstractmethod
    def detect(self, signal, **kwargs):
        """Detect beats in the given signal"""
        pass
