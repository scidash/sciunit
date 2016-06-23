import math

import quantities as pq

import sciunit
import sciunit.utils as utils

class InsufficientDataScore(sciunit.NoneScore):
    """A score returned when the model or test data 
    is insufficient to score the test."""
    
    def __init__(self, score, related_data={}):
        super(InsufficientDataScore,self).__init__(score, 
                                                   related_data=related_data)

    @property
    def sort_key(self):
        return None

    def __str__(self):
        return 'Insufficient Data'


class BooleanScore(sciunit.Score):
    """
    A boolean score. Must be True or False.
    """
    
    def __init__(self, score, related_data={}):
        if isinstance(score,Exception) or score in [True,False]:
            super(BooleanScore,self).__init__(score, related_data=related_data)
        else:
            raise sciunit.InvalidScoreError("Score must be True or False.")
        
    _description = ('True if the observation and prediction were '
                   'sufficiently similar; False otherwise')

    @classmethod
    def compute(cls, observation, prediction):
        """
        Computes whether the observation equals the prediction.
        """
        return BooleanScore(observation == prediction)

    @property
    def sort_key(self):
        """Returns 1.0 for a Boolean score of True, 
        and 0.0 for a score of False."""
        
        if self.score == True:
            return 1.0
        elif self.score == False:
            return 0.0

    def __str__(self):
        if self.score == True:
            return 'Pass'
        elif self.score == False:
            return 'Fail'


class ZScore(sciunit.Score):
    """
    A Z score. A float indicating standardized difference 
    from a reference mean.
    """
    
    def __init__(self, score, related_data={}):
        if not isinstance(score, Exception) and not isinstance(score, float):
            raise sciunit.InvalidScoreError("Score must be a float.")
        else:
            super(ZScore,self).__init__(score, related_data=related_data)

    @classmethod
    def compute(cls, observation, prediction):
        """
        Computes a z-score from an observation and a prediction.
        """
        assert type(observation) is dict
        assert type(prediction) is dict
        try:
            p_value = prediction['mean'] # Use the prediction's mean.  
        except (TypeError,KeyError): # If there isn't one...
            try:
                p_value = prediction['value'] # Use the prediction's value.  
            except TypeError: # If there isn't one...
                p_value = prediction # Use the prediction (assume it is numeric).
        o_mean = observation['mean']
        o_std = observation['std']
        value = (p_value - o_mean)/o_std
        value = utils.assert_dimensionless(value)
        return ZScore(value)

    _description = ('The difference between the means of the observation and '
                   'prediction divided by the standard deviation of the '
                   'observation')

    @property
    def sort_key(self):
        """Returns 1.0 for a z-score of 0, falling to 0.0 for extremely positive
        or negative values."""

        cdf = (1.0 + math.erf(self.score / math.sqrt(2.0))) / 2.0
        return 1 - 2*math.fabs(0.5 - cdf)

    def __str__(self):
        return 'Z = %.2f' % self.score


class CohenDScore(sciunit.Score):
    """
    A Cohen's D score. A float indicating difference 
    between two means normalized by the pooled standard deviation.
    """
    
    def __init__(self, score, related_data={}):
        if not isinstance(score, Exception) and not isinstance(score, float):
            raise sciunit.InvalidScoreError("Score must be a float.")
        else:
            super(CohenDScore,self).__init__(score, related_data=related_data)

    @classmethod
    def compute(cls, observation, prediction):
        """
        Computes a Cohen's D from an observation and a prediction.
        """
        assert type(observation) is dict
        assert type(prediction) is dict
        p_mean = prediction['mean'] # Use the prediction's mean.  
        p_std = prediction['std']
        o_mean = observation['mean']
        o_std = observation['std']
        try: # Try to pool taking samples sizes into account.  
            p_n = prediction['n']
            o_n = observation['n']
            s = (((p_n-1)*(p_std**2) + (o_n-1)*(o_std**2))/(p_n+o_n-2))**0.5
        except KeyError: # If sample sizes are not available.
            s = (p_std**2 + o_std**2)**0.5
        value = (p_mean - o_mean)/s
        value = utils.assert_dimensionless(value)
        return CohenDScore(value)

    _description = ("The Cohen's D between the prediction and the observation")

    @property
    def sort_key(self):
        """Returns 1.0 for a D of 0, falling to 0.0 for extremely positive
        or negative values."""

        cdf = (1.0 + math.erf(self.score / sqrt(2.0))) / 2.0
        return 1 - 2*math.fabs(0.5 - cdf)

    def __str__(self):
        return 'D = %.2f' % self.score


class RatioScore(sciunit.Score):
    """
    A ratio of two numbers score. Usually the prediction divided by
    the observation.  
    """

    def __init__(self, score, related_data={}):
        if not isinstance(score, Exception) and not isinstance(score, float):
            raise sciunit.InvalidScoreError("Score must be a float.")
        else:
            super(RatioScore,self).__init__(score, related_data=related_data)

    _description = ('The ratio between the prediction and the observation')

    @classmethod
    def compute(cls, observation, prediction, key=None):
        """
        Computes a ratio from an observation and a prediction.
        """
        assert type(observation) is dict
        assert type(prediction) is dict

        def extract_mean_or_value(observation, prediction):
            values = {}
            for name,data in [('observation',observation),
                              ('prediction',prediction)]:
                if key is not None:
                    values[name] = data[key]
                else:
                    try:
                        values[name] = data['mean'] # Use the mean.  
                    except KeyError: # If there isn't a mean...
                        try:
                            values[name] = data['value'] # Use the value.  
                        except KeyError:
                            raise KeyError(("%s has neither a mean nor a single "
                                            "value" % name))
            return values['observation'], values['prediction']

        pred, obs = extract_mean_or_value(observation, prediction)
        value = pred / obs
        value = utils.assert_dimensionless(value)
        return RatioScore(value)

    @property
    def sort_key(self):
        """Returns 1.0 for a ratio of 1, falling to 0.0 for extremely small
        or large values."""

        return 1 - min(1,math.fabs(math.log10(self.score)))

    def __str__(self):
        return 'Ratio = %.2f' % self.score


class PercentScore(sciunit.Score):
    """
    A percent score. A float in the range [0,0,100.0] where higher is better.
    """

    def __init__(self, score, related_data={}):
        if not isinstance(score, Exception) and not isinstance(score, float):
            raise sciunit.InvalidScoreError("Score must be a float.")
        elif score < 0.0 or score > 100.0:
            raise sciunit.InvalidScoreError(("Score of %f must be in "
                                             "range 0.0-100.0" % score))
        else:
            super(PercentScore,self).__init__(score, related_data=related_data)

    _description = ('100.0 is considered perfect agreement between the '
                   'observation and the prediction. 0.0 is the worst possible '
                   'agreement')


    @property
    def sort_key(self):
        """Returns 1.0 for a percent score of 100, and 0.0 for 0."""

        return self.score/100
        
    def __str__(self):
        return '%.1f%%' % self.score


class FloatScore(sciunit.Score):
    """
    A float score. A float with any value.
    """

    def __init__(self, score, related_data={}):
        if not isinstance(score, Exception) and \
           not isinstance(score, float) and \
           not (isinstance(score, pq.Quantity) and score.size==1):
            raise sciunit.InvalidScoreError("Score must be a float.")
        else:
            super(FloatScore,self).__init__(score, related_data=related_data)

    _description = ('There is no canonical mapping between this score type and '
                   'a measure of agreement between the observation and the '
                   'prediction')

    
    @classmethod
    def compute_ssd(cls, observation, prediction):
        """
        Computes a sum-squared difference from an observation and a prediction.
        """
        value = ((observation - prediction)**2).sum() # The sum of the 
                                                      # squared differences.
        score = FloatScore(value)
        score.value = value
        return score
     
    def __str__(self):
        return '%.3g' % self.score

