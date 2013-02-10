from sciunit import ScoreMap

class BooleanScoreMap(ScoreMap):
    def __init__(self,stats,related_data):
        if not isinstance(stats,tuple) or len(stats) is not 3:
            raise InvalidScoreMapError("A tuple of value, mean, and standard deviation must be provided.")
        ScoreMap.__init__(self,stats,related_data)

    def score(self,**kwargs):
        z_thresh = kwargs['z_thresh'] 
        r_mean = self.reference_stats['mean']
        r_stdev = self.reference_stats['stdev']
        value = self.result_stats['value']
        return (-z_thresh*r_stdev) < (value-r_mean) < (z_thresh*r_stdev)

class ZScoreMap(ScoreMap):
    def __init__(self,stats,related_data):
        if not isinstance(stats,tuple) or len(stats) is not 3:
            raise InvalidScoreMapError("A tuple of value, mean, and standard deviation must be provided.")
        ScoreMap.__init__(self,stats,related_data)

    def score(self,**kwargs):
        r_mean = self.reference_stats['mean']
        r_stdev = self.reference_stats['stdev']
        value = self.result_stats['value']
        return norm.cdf(value,r_mean_,r_stdev)