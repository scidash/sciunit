from .scores import BooleanScore,RatioScore,ZScore,FloatScore
from .utils import assert_dimensionless

"""
Each 'compute' function takes and observation and a prediction
and returns a score.
"""

def compute_equality(observation,prediction):
    """
    Computes whether the observation and prediction are equal.
    """
    value = observation==prediction
    return BooleanScore(value)


def compute_ratio(observation, prediction):
    """
    Computes a ratio from an observation and a prediction.
    """
    m_value = prediction['value']
    r_mean = observation['mean']
    
    value = (m_value+0.0)/r_mean
    return RatioScore(value)


def compute_zscore(observation, prediction):
    """
    Computes a z-score from an observation and a prediction.
    """
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
    value = assert_dimensionless(value)
    return ZScore(value)

def compute_ssd(observation, prediction):
    """
    Computes a sum-squared difference from an observation and a prediction.
    """
    value = sum((observation - prediction)**2) # The sum of the 
                                               # squared differences.
    return FloatScore(value)
        

