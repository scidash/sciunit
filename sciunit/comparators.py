"""Functions for comparison of predictions and observations."""

def ratio(observation, prediction):
    m_value = output_stats['value']
    r_mean = reference_stats['mean']
    result = (m_value+0.0)/r_mean
    return result

def zscore(observation, prediction):
    p_value = prediction['mean']
    o_mean = observation['mean']
    o_std = observation['std']
    try:
        result = (p_value - o_mean)/o_std
    except TypeError as e:
        result = e
    return result

def z_to_boolean(z,params={'thresh':2}):
    """Converts a raw ZScore to a raw BooleanScore."""  
    thresh = params['thresh'] # +/- Threshold within which Z must stay to pass.  
    boolean = -thresh <= Z.score <= thresh
    return boolean
    