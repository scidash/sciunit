from quantities.dimensionality import Dimensionality
from quantities.quantity import Quantity

"""Functions for comparison of predictions and observations."""

def dimensionless(value):
    """Test for dimensionlessness of input."""
    if type(value) is Quantity:
        if value.dimensionality == Dimensionality({}):
            value = value.base.item()
        else:
            raise TypeError("Score value %s must be dimensionless" % value)
    return value

def ratio(observation, prediction):
    """Computes a ratio from an observation and a prediction."""
    m_value = prediction['value']
    r_mean = observation['mean']
    result = (m_value+0.0)/r_mean
    return result

def zscore(observation, prediction):
    """Computes a z-score from an observation and a prediction."""
    try:
        p_value = prediction['mean']
    except (TypeError,KeyError):
        try:
            p_value = prediction['value']
        except TypeError:
            p_value = prediction
    o_mean = observation['mean']
    o_std = observation['std']
    try:
        result = (p_value - o_mean)/o_std
        result = dimensionless(result)
    except (TypeError,AssertionError) as e:
        result = e
    return result

def z_to_boolean(z,params={'thresh':2}):
    """Converts a raw ZScore to a raw BooleanScore."""  
    thresh = params['thresh'] # +/- Threshold within which Z must stay to pass.  
    boolean = -thresh <= Z.score <= thresh
    return boolean
    