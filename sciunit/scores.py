from sciunit import Score,ErrorScore,InvalidScoreError

class BooleanScore(Score):
    """A boolean score."""
    
    def __init__(self, score, related_data={}):
        if (score == True or score == False):
            super(BooleanScore,self).__init__(score, related_data=related_data)
        elif isinstance(score,Exception):
            self.__class__ = ErrorScore
            super(ErrorScore,self).__init__(score)
        else:
            raise InvalidScoreError("Score must be True or False.")
        
    normalized = True

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
    """A Z score."""
    
    def __init__(self, score, related_data={}):
        if isinstance(score, float):
            super(ZScore,self).__init__(score, related_data=related_data)
        elif isinstance(score,Exception):
            self.__class__ = ErrorScore
            super(ErrorScore,self).__init__(score)
        else:
            raise InvalidScoreError("Score must be a float.")
        
    def __str__(self):
        return u'%.2f' % self.score

    