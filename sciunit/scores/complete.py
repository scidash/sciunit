"""Score types for tests that completed successfully.

These include various representations of goodness-of-fit.
"""

from __future__ import division

import math

import numpy as np
import quantities as pq

from sciunit import utils
from sciunit import errors
from .base import Score
from .incomplete import InsufficientDataScore


class BooleanScore(Score):
    """A boolean score, which must be True or False."""

    _allowed_types = (bool,)

    _description = ('True if the observation and prediction were '
                    'sufficiently similar; False otherwise')

    @classmethod
    def compute(cls, observation, prediction):
        """Compute whether the observation equals the prediction."""
        return BooleanScore(observation == prediction)

    @property
    def norm_score(self):
        """Return 1.0 for a True score and 0.0 for False score."""
        return 1.0 if self.score else 0.0

    def __str__(self):
        return 'Pass' if self.score else 'Fail'


class ZScore(Score):
    """A Z score.

    A float indicating standardized difference
    from a reference mean.
    """

    _allowed_types = (float,)

    _description = ('The difference between the means of the observation and '
                    'prediction divided by the standard deviation of the '
                    'observation')

    @classmethod
    def compute(cls, observation, prediction):
        """Compute a z-score from an observation and a prediction."""
        assert isinstance(observation, dict)
        try:
            p_value = prediction['mean']  # Use the prediction's mean.
        except (TypeError, KeyError, IndexError):  # If there isn't one...
            try:
                p_value = prediction['value']  # Use the prediction's value.
            except (TypeError, IndexError):  # If there isn't one...
                p_value = prediction  # Use the prediction (assume numeric).
        o_mean = observation['mean']
        o_std = observation['std']
        value = (p_value - o_mean)/o_std
        value = utils.assert_dimensionless(value)
        if np.isnan(value):
            score = InsufficientDataScore('One of the input values was NaN')
        else:
            score = ZScore(value)
        return score

    @property
    def norm_score(self):
        """Return the normalized score.

        Equals 1.0 for a z-score of 0, falling to 0.0 for extremely positive
        or negative values.
        """
        cdf = (1.0 + math.erf(self.score / math.sqrt(2.0))) / 2.0
        return 1 - 2*math.fabs(0.5 - cdf)

    def __str__(self):
        return 'Z = %.2f' % self.score


class CohenDScore(ZScore):
    """A Cohen's D score.

    A float indicating difference
    between two means normalized by the pooled standard deviation.
    """

    _description = ("The Cohen's D between the prediction and the observation")

    @classmethod
    def compute(cls, observation, prediction):
        """Compute a Cohen's D from an observation and a prediction."""
        assert isinstance(observation, dict)
        assert isinstance(prediction, dict)
        p_mean = prediction['mean']  # Use the prediction's mean.
        p_std = prediction['std']
        o_mean = observation['mean']
        o_std = observation['std']
        try:  # Try to pool taking samples sizes into account.
            p_n = prediction['n']
            o_n = observation['n']
            s = (((p_n-1)*(p_std**2) + (o_n-1)*(o_std**2))/(p_n+o_n-2))**0.5
        except KeyError:  # If sample sizes are not available.
            s = (p_std**2 + o_std**2)**0.5
        value = (p_mean - o_mean)/s
        value = utils.assert_dimensionless(value)
        return CohenDScore(value)

    def __str__(self):
        return 'D = %.2f' % self.score


class RatioScore(Score):
    """A ratio of two numbers.

    Usually the prediction divided by
    the observation.
    """

    _allowed_types = (float,)

    _description = ('The ratio between the prediction and the observation')

    def _check_score(self, score):
        if score < 0.0:
            raise errors.InvalidScoreError(("RatioScore was initialized with "
                                            "a score of %f, but a RatioScore "
                                            "must be non-negative.") % score)

    @classmethod
    def compute(cls, observation, prediction, key=None):
        """Compute a ratio from an observation and a prediction."""
        assert isinstance(observation, (dict, float, int, pq.Quantity))
        assert isinstance(prediction, (dict, float, int, pq.Quantity))

        obs, pred = cls.extract_means_or_values(observation, prediction,
                                                key=key)
        value = pred / obs
        value = utils.assert_dimensionless(value)
        return RatioScore(value)

    @property
    def norm_score(self):
        """Return 1.0 for a ratio of 1, falling to 0.0 for extremely small
        or large values."""
        score = math.log10(self.score)
        cdf = (1.0 + math.erf(score / math.sqrt(2.0))) / 2.0
        return 1 - 2*math.fabs(0.5 - cdf)

    def __str__(self):
        return 'Ratio = %.2f' % self.score


class PercentScore(Score):
    """A percent score.

    A float in the range [0,0,100.0] where higher is better.
    """

    _description = ('100.0 is considered perfect agreement between the '
                    'observation and the prediction. 0.0 is the worst possible'
                    ' agreement')

    def _check_score(self, score):
        if not (0.0 <= score <= 100.0):
            raise errors.InvalidScoreError(("Score of %f must be in "
                                            "range 0.0-100.0" % score))

    @property
    def norm_score(self):
        """Return 1.0 for a percent score of 100, and 0.0 for 0."""
        return float(self.score)/100

    def __str__(self):
        return '%.1f%%' % self.score


class FloatScore(Score):
    """A float score.

    A float with any value.
    """

    _allowed_types = (float, pq.Quantity,)

    def _check_score(self, score):
        if isinstance(score, pq.Quantity) and score.size != 1:
            raise errors.InvalidScoreError("Score must have size 1.")

    _description = ('There is no canonical mapping between this score type and'
                    ' a measure of agreement between the observation and the '
                    'prediction')

    @classmethod
    def compute_ssd(cls, observation, prediction):
        """Compute sum-squared diff between observation and prediction."""
        # The sum of the squared differences.
        value = ((observation - prediction)**2).sum()
        score = FloatScore(value)
        return score

    def __str__(self):
        return '%.3g' % self.score
