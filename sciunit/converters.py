"""
Classes for converting from the output of a model/data comparison
to the value required for particular score type.
"""

from string import Template
import sciunit.scores as scores

class Converter(object):
    """
    Base converter class.  
    Only derived classes should be used in applications.
    """

    @property
    def description(self):
        s = ' '.join([si.strip() for si in self.__doc__.split('\n')]).strip()
        t = Template(s)
        s = t.safe_substitute(self.__dict__)
        return s

    def _convert(self,score):
        """
        Takes the score attribute of a score instance
        and recasts it as instance of another score type.  
        """
        NotImplementedError(("The '_convert' method for %s "
                                    "it not implemented." %
                                    self.__class__.__name__))

    def convert(self,score):
        new_score = self._convert(score.score)
        for key,value in score.__dict__.items():
            if key != 'score':
                setattr(new_score,key,value)
        return new_score


class NoConversion(Converter):
    """
    Applies no conversion.
    """    

    def _convert(self,score):
        return score


class AtMostToBoolean(Converter):
    """
    Converts a score to pass if its value is at most $cutoff, otherwise False.
    """
    def __init__(self,cutoff):
        self.cutoff = cutoff
    
    def _convert(self,score):
        return scores.BooleanScore(score <= self.cutoff)


class AtLeastToBoolean(Converter):
    """
    Converts a score to Pass if its value is at least $cutoff, otherwise False.
    """
    def __init__(self,cutoff):
        self.cutoff = cutoff
    
    def _convert(self,score):
        return scores.BooleanScore(score >= self.cutoff)


class RangeToBoolean(Converter):
    """
    Converts a score to Pass if its value is within the range
    [$low_cutoff,$high_cutoff], otherwise Fail.
    """
    def __init__(self,low_cutoff,high_cutoff):
        self.low_cutoff = low_cutoff
        self.high_cutoff = high_cutoff

    def _convert(self,score):
        return scores.BooleanScore(self.low_cutoff <= score <= self.high_cutoff)


