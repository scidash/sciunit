from sciunit import Score,ErrorScore,InvalidScoreError
        
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

    