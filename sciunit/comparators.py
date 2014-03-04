import sciunit
import sciunit.scores

def ratio(output_stats,reference_stats):
    m_value = output_stats['value']
    r_mean = reference_stats['mean']
    result = (m_value+0.0)/r_mean
    return result

def zscore(sciunit.Comparator):
    m_value = output_stats['value']
    r_mean = reference_stats['mean']
    r_std = reference_stats['std']
    try:
        result = (m_value - r_mean)/r_std
    except TypeError,e:
        result = e
    return result

def z_to_boolean(z,params={'thresh':2}):
    """Converts a raw ZScore to a raw BooleanScore."""  
    thresh = params['thresh'] # +/- Threshold within which Z must stay to pass.  
    boolean = -thresh <= Z.score <= thresh
    return boolean
    