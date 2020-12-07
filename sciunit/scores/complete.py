"""Score types for tests that completed successfully.

These include various representations of goodness-of-fit.
"""

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

    _best = True

    _worst = False

    @classmethod
    def compute(cls, observation: dict, prediction: dict) -> 'BooleanScore':
        """Compute whether the observation equals the prediction.

        Returns:
            BooleanScore: Boolean score of the observation equals the prediction.
        """
        return BooleanScore(observation == prediction)

    @property
    def norm_score(self) -> float:
        """Return 1.0 for a True score and 0.0 for False score.

        Returns:
            float: 1.0 for a True score and 0.0 for False score.
        """
        return 1.0 if self.score else 0.0

    def __str__(self) -> str:
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

    _best = 0.0  # A Z-Score of 0.0 is best

    _worst = np.inf  # A Z-score of infinity (or negative infinity) is worst

    @classmethod
    def compute(cls, observation: dict, prediction: dict) -> 'ZScore':
        """Compute a z-score from an observation and a prediction.

        Returns:
            ZScore: The computed Z-Score.
        """
        assert isinstance(observation, dict),\
            "Observation must be a dict when using ZScore, not type %s" \
            % type(observation)
        try:
            p_value = prediction['mean']  # Use the prediction's mean.
        except (TypeError, KeyError, IndexError):  # If there isn't one...
            try:
                p_value = prediction['value']  # Use the prediction's value.
            except (TypeError, IndexError):  # If there isn't one...
                p_value = prediction  # Use the prediction (assume numeric).
        try:
            o_mean = observation['mean']
            o_std = observation['std']
        except KeyError:
            error = ("Observation must have keys 'mean' and 'std' "
                     "when using ZScore")
            return InsufficientDataScore(error)
        if o_std <= 0:
            error = 'Observation standard deviation must be > 0'
            return InsufficientDataScore(error)
        value = (p_value - o_mean)/o_std
        value = utils.assert_dimensionless(value)
        if np.isnan(value):
            error = 'One of the input values was NaN'
            return InsufficientDataScore(error)
        score = ZScore(value)
        return score

    @property
    def norm_score(self) -> float:
        """Return the normalized score.

        Equals 1.0 for a z-score of 0, falling to 0.0 for extremely positive
        or negative values.
        """
        cdf = (1.0 + math.erf(self.score / math.sqrt(2.0))) / 2.0
        return 1 - 2*math.fabs(0.5 - cdf)

    def __str__(self) -> str:
        return 'Z = %.2f' % self.score


class CohenDScore(ZScore):
    """A Cohen's D score.

    A float indicating difference
    between two means normalized by the pooled standard deviation.
    """

    _description = ("The Cohen's D between the prediction and the observation")

    _best = 0.0

    _worst = np.inf

    @classmethod
    def compute(cls, observation: dict, prediction: dict) -> 'CohenDScore':
        """Compute a Cohen's D from an observation and a prediction.

        Returns:
            CohenDScore: The computed Cohen's D Score.
        """
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

    def __str__(self) -> str:
        return 'D = %.2f' % self.score


class RatioScore(Score):
    """A ratio of two numbers.

    Usually the prediction divided by
    the observation.
    """

    _allowed_types = (float,)

    _description = ('The ratio between the prediction and the observation')

    _best = 1.0  # A RatioScore of 1.0 is best

    _worst = np.inf

    def _check_score(self, score):
        if score < 0.0:
            raise errors.InvalidScoreError(("RatioScore was initialized with "
                                            "a score of %f, but a RatioScore "
                                            "must be non-negative.") % score)

    @classmethod
    def compute(cls, observation: dict, prediction: dict, key=None) -> 'RatioScore':
        """Compute a ratio from an observation and a prediction.

        Returns:
            RatioScore: A RatioScore of ratio from an observation and a prediction.
        """
        assert isinstance(observation, (dict, float, int, pq.Quantity))
        assert isinstance(prediction, (dict, float, int, pq.Quantity))

        obs, pred = cls.extract_means_or_values(observation, prediction,
                                                key=key)
        value = pred / obs
        value = utils.assert_dimensionless(value)
        return RatioScore(value)

    @property
    def norm_score(self) -> float:
        """Return 1.0 for a ratio of 1, falling to 0.0 for extremely small or large values.

        Returns:
            float: The value of the norm score.
        """
        score = math.log10(self.score)
        cdf = (1.0 + math.erf(score / math.sqrt(2.0))) / 2.0
        return 1 - 2*math.fabs(0.5 - cdf)

    def __str__(self):
        return 'Ratio = %.2f' % self.score


class PercentScore(Score):
    """A percent score.

    A float in the range [0, 100.0] where higher is better.
    """

    _description = ('100.0 is considered perfect agreement between the '
                    'observation and the prediction. 0.0 is the worst possible'
                    ' agreement')

    _best = 100.0

    _worst = 0.0

    def _check_score(self, score):
        if not (0.0 <= score <= 100.0):
            raise errors.InvalidScoreError(("Score of %f must be in "
                                            "range 0.0-100.0" % score))

    @property
    def norm_score(self) -> float:
        """Return 1.0 for a percent score of 100, and 0.0 for 0.

        Returns:
            float: 1.0 if the percent score is 100, else 0.0.
        """
        return float(self.score)/100

    def __str__(self) -> str:
        return '%.1f%%' % self.score


class FloatScore(Score):
    """A float score.

    A float with any value.
    """

    _allowed_types = (float, pq.Quantity,)

    # The best value is indeterminate without more context.
    # But some float value must be supplied to use methods like Test.ace().
    _best = 0.0

    # The best value is indeterminate without more context.
    _worst = 0.0

    def _check_score(self, score):
        if isinstance(score, pq.Quantity) and score.size != 1:
            raise errors.InvalidScoreError("Score must have size 1.")

    _description = ('There is no canonical mapping between this score type and'
                    ' a measure of agreement between the observation and the '
                    'prediction')

    @classmethod
    def compute_ssd(cls, observation: dict, prediction: dict) -> Score:
        """Compute sum-squared diff between observation and prediction.

        Args:
            observation (dict): The observation to be used for computing the sum-squared diff.
            prediction (dict): The prediction to be used for computing the sum-squared diff.

        Returns:
            Score: The sum-squared diff between observation and prediction.
        """
        # The sum of the squared differences.
        value = ((observation - prediction)**2).sum()
        score = FloatScore(value)
        return score

    def __str__(self) -> str:
        return '%.3g' % self.score


class RandomScore(FloatScore):
    """A random score in [0,1].

    This has no scientific value and should only be used for debugging
    purposes. For example, one might assign a random score under some error
    condition to move forward with an application that requires a numeric
    score, and use the presence of a RandomScore in the output as an
    indication of an internal error.
    """

    _allowed_types = (float,)

    _description = ('There is a random number in [0,1] and has no relation to '
                    'the prediction or the observation')

    def __str__(self) -> str:
        return '%.3g' % self.score

    
class CorrelationScore(Score):
    """A correlation score.
    A float in the range [-1.0, 1.0] representing the correlation coefficient.
    """

    _description = ('A correlation of -1.0 shows a perfect negative correlation,'
                    'while a correlation of 1.0 shows a perfect positive correlation.'
                    'A correlation of 0.0 shows no linear relationship between the movement of the two variables')

    _best = 1.0
    
    _worst = -1.0

    def _check_score(self, score):
        if not (-1.0 <= score <= 1.0):
            raise errors.InvalidScoreError(("Score of %.3g must be in "
                                            "range [-1.0, 1.0]" % score))
    @classmethod
    def compute(cls, observation, prediction):
        """Compute whether the observation equals the prediction."""
        return CorrelationScore(float(np.corrcoef(observation, prediction)[0, 1]))

    def __str__(self):
        return '%.3g' % self.score
    
