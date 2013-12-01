import sciunit

class BooleanScore(sciunit.Score):
    """A boolean score."""
    def __init__(self, score):
        if not (isinstance(score, bool) or type(score).__name__ == 'bool_'):
            raise sciunit.InvalidScoreError("Score must be a boolean.")
        super(BooleanScore,self).__init__(score)
    def __str__(self):
        if self.score == True:
            return u'PASS'
        elif self.score == False:
            return u'FAIL'
        else:
            return u'N/A'

class ZScore(sciunit.Score):
    """A Z score."""
    def __init__(self, score):
        if not isinstance(score, float):
            raise sciunit.InvalidScoreError("Score must be a float.")
        super(ZScore,self).__init__(score)
    def __str__(self):
        return u'%.2f' % self.score

class RatioScore(sciunit.Score):
    """A ratio score."""
    def __init__(self, score):
        if not isinstance(score, float):
            raise sciunit.InvalidScoreError("Score must be a float.")
        super(RatioScore,self).__init__(score)
    def __str__(self):
        return u'%.2f' % self.score

        