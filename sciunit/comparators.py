from sciunit import Comparator
from sciunit.scores import BooleanScore,ZScore,RatioScore
from scipy.stats import norm

class RatioComparator(Comparator):
    """Returns a score indicating the ratio of candidate to reference means."""  
    def __init__(self,*args,**kwargs):
        self.required_candidate_stats += ('value',)
        self.required_reference_stats += ('mean',)
        super(RatioComparator,self).__init__(*args,**kwargs)

    score_type = RatioScore

    def compute(self,**kwargs):
        m_value = self.candidate_stats['value']
        r_mean = self.reference_stats['mean']
        return (m_value+0.0)/r_mean

class ZComparator(Comparator):
    """Returns a score indicating the Z-score of the candidate value relative to the 
    reference mean and standard deviation."""  
    def __init__(self,*args,**kwargs):
        self.required_candidate_stats += ('value',)
        self.required_reference_stats += ('mean','std',)    
        super(ZComparator,self).__init__(*args,**kwargs)

    score_type = ZScore

    def compute(self,**kwargs):
        m_value = self.candidate_stats['value']
        r_mean = self.reference_stats['mean']
        r_std = self.reference_stats['std']
        return (m_value - r_mean)/r_std

"""Converters for converting from one (raw) score to another kind of (raw) score.
The converter attribute of a Comparator or a Test can be set to one of these."""

def ZScoreToBooleanScore(self,Z,params={'thresh':2}):
    """Converts a ZScore class to a BooleanScore class."""  
    thresh = params['thresh'] # +/- Threshold within which Z must stay to pass.  
    boolean = -thresh <= Z.score <= thresh
    return BooleanScore(boolean)