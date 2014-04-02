from sciunit import Score,ErrorScore,InvalidScoreError

class NoneScore(Score):
    """A None score.  Indicates that the model has not been checked to see if
    it has the capabilities required by the test."""

    def __init__(self, score, related_data={}):
        if isinstance(score,Exception) or score is None:
            super(NoneScore,self).__init__(score, related_data=related_data)
        else:
            raise InvalidScoreError("Score must be None.")

class TBDScore(NoneScore):
    """A TBD (to be determined) score. Indicates that the model has capabilities 
    required by the test but has not yet taken it."""

    def __init__(self, score, related_data={}):
        super(TBDScore,self).__init__(score, related_data=related_data)
        
class NAScore(NoneScore):
    """A N/A (not applicable) score. Indicates that the model doesn't have the 
    capabilities that the test requires."""

    def __init__(self, score, related_data={}):
        super(NAScore,self).__init__(score, related_data=related_data)
        
class BooleanScore(Score):
    """A boolean score. Must be True or False."""
    
    def __init__(self, score, related_data={}):
        if isinstance(score,Exception) or score in [True,False]:
            super(BooleanScore,self).__init__(score, related_data=related_data)
        else:
            raise InvalidScoreError("Score must be True or False.")
        
    @property
    def sort_key(self):
        if self.score == True:
            return 1.0
        elif self.score == False:
            return 0.0
        else:
            return 'N/A'

    def __str__(self):
        if self.score == True:
            return 'Pass'
        elif self.score == False:
            return 'Fail'
        else:
            return 'N/A'


class ZScore(Score):
    """A Z score. A float indicating standardized difference 
    from a reference mean."""
    
    def __init__(self, score, related_data={}):
        if isinstance(score, Exception) or isinstance(score, float):
            super(ZScore,self).__init__(score, related_data=related_data)
        else:
            raise InvalidScoreError("Score must be a float.")
        
    def __str__(self):
        return u'%.2f' % self.score

    