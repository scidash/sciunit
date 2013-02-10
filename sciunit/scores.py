from sciunit import Score

class BooleanScore(Score):
    """A boolean score."""
    def __init__(self, score, related_data):
        if not isinstance(score, bool):
            raise InvalidScoreError("Score must be a boolean.")
        Score.__init__(self, score, related_data)

class ZScore(Score):
    """A Z score."""
    def __init__(self, score, related_data):
        if not isinstance(score, float):
            raise InvalidScoreError("Score must be a float.")
        Score.__init__(self, score, related_data)

