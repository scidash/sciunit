import sciunit

class BooleanScore(sciunit.Score):
    """A boolean score."""
    
    def __init__(self, score):
        if not (score == True or score == False):
            raise sciunit.InvalidScoreError("Score must be True or False.")
        super(BooleanScore, self).__init__(score)

    normalized = True

    @property
    def sort_key(self):
        if self.score == True:
            return 1.0
        else:
            return 0.0

    def __str__(self):
        if self.score == True:
            return 'PASS'
        elif self.score == False:
            return 'FAIL'
