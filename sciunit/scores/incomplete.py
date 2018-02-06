"""
Score types for tests that did not complete successfully.
These include details about the various possible reasons
that a particular combination of model and test could not be completed.
"""  

from .base import Score
from sciunit.errors import InvalidScoreError

class ErrorScore(Score):
    """A score returned when an error occurs during testing."""
    
    @property
    def sort_key(self):
        return 0.0

    @property
    def summary(self):
        """Summarize the performance of a model on a test."""
        return "=== Model %s did not complete test %s due to error '%s'. ===" % \
               (str(self.model), str(self.test), str(self.score))

    def _describe(self):
        return self.summary

    def __str__(self):
        return 'Error'


class NoneScore(Score):
    """A None score.  Usually indicates that the model has not been 
    checked to see if it has the capabilities required by the test."""

    def __init__(self, score, related_data=None):
        if isinstance(score,str) or score is None:
            super(NoneScore,self).__init__(score, related_data=related_data)
        else:
            raise InvalidScoreError("Score must be a string or None")

    @property
    def sort_key(self):
        return None

    def __str__(self):
        return 'Unknown'


class TBDScore(NoneScore):
    """A TBD (to be determined) score. Indicates that the model has capabilities 
    required by the test but has not yet taken it."""

    def __init__(self, score, related_data=None):
        super(TBDScore,self).__init__(score, related_data=related_data)

    @property
    def sort_key(self):
        return None

    def __str__(self):
        return 'TBD'

        
class NAScore(NoneScore):
    """A N/A (not applicable) score. Indicates that the model doesn't have the 
    capabilities that the test requires."""

    def __init__(self, score, related_data=None):
        super(NAScore,self).__init__(score, related_data=related_data)

    @property
    def sort_key(self):
        return None

    def __str__(self):
        return 'N/A'

class InsufficientDataScore(NoneScore):
    """A score returned when the model or test data 
    is insufficient to score the test."""
    
    @property
    def sort_key(self):
        return None

    def __str__(self):
        return 'Insufficient Data'