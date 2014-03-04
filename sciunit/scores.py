import sciunit

class ErrorScore(sciunit.Score):
    """A score returned when an error occurs during testing."""

    def __init__(self, score, *args, **kwargs):
        if not isinstance(score, Exception):
            raise sciunit.InvalidScoreError("Score must be an Exception.")
        super(ErrorScore,self).__init__(score, *args, **kwargs)

    def __str__(self):
        return u'"%s: %s"' % (self.score.__class__.__name__,self.score)

class BooleanScore(sciunit.Score):
    """A boolean score."""
    
    def __init__(self, score, *args, **kwargs):
        if (score == True or score == False):
            super(BooleanScore,self).__init__(score, *args, **kwargs)
        elif isinstance(score,Exception):
            self.__class__ = ErrorScore
            super(ErrorScore,self).__init__(score, *args, **kwargs)
        else:
            raise sciunit.InvalidScoreError("Score must be True or False.")
        
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


class ZScore(sciunit.Score):
    """A Z score."""
    
    def __init__(self, score, *args, **kwargs):
        if isinstance(score, float):
            super(ZScore,self).__init__(score, *args, **kwargs)
        elif isinstance(score,Exception):
            self.__class__ = ErrorScore
            super(ErrorScore,self).__init__(score, *args, **kwargs)
        else:
            raise sciunit.InvalidScoreError("Score must be a float.")
        
    def __str__(self):
        return u'%.2f' % self.score
=======
            return 0.0
>>>>>>> bf3616fa571baee622a4fa846477760d02179765

    def __str__(self):
        if self.score == True:
            return 'PASS'
        elif self.score == False:
            return 'FAIL'
