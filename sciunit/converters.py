"""
Classes for converting from the output of a model/data comparison
to the value required for particular score type.
"""

from string import Template
from .scores import BooleanScore

class Converter(object):
    """
    Base converter class.  
    Only derived classes should be used in applications.
    """

    @property
    def description(self):
        s = self.__doc__.strip().replace('\n','')
        t = Template(s)
        s = t.safe_substitute(self.__dict__)
        return s

    def convert(self,z):
        return NotImplementedError(("The 'convert' method for %s "
                                    "it not implemented." %
                                    self.__class__.__name__))


class NoConversion(Converter):
    """
    Applies no conversion.
    """    

    

    def convert(self,score):
        return score


class AtMostToBoolean(Converter):
    """
    Converts a score to pass if its value is at most $cutoff, otherwise False.
    """
    def __init__(self,cutoff):
        self.cutoff = cutoff

    @property
    def description(self):
        return "Passes if the score is <=%.3g" % self.cutoff
        
    def convert(self,score):
        return BooleanScore(score.score <= self.cutoff)


class AtLeastToBoolean(Converter):
    """
    Converts a score to Pass if its value is at least $cutoff, otherwise False.
    """
    def __init__(self,cutoff):
        self.cutoff = cutoff

    @property
    def description(self):
        return "Passes if the score is >=%.3g" % self.cutoff
        
    def convert(self,score):
        return BooleanScore(score.score >= self.cutoff)


class RangeToBoolean(Converter):
    """
    Converts a score to Pass if its value is within the range
    [$low_cutoff,$high_cutoff], otherwise Fail.
    """
    def __init__(self,low_cutoff,high_cutoff):
        self.low_cutoff = low_cutoff
        self.high_cutoff = high_cutoff

    @property
    def description(self):
        return "Passes if the score is >=%.3g and <=%.3g" % \
            (self.low_cutoff, self.high_cutoff)

    def convert(self,score):
        return BooleanScore(self.low_cutoff <= score.score <= self.high_cutoff)

    