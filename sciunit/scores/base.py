"""Base class for SciUnit scores."""

from copy import copy

import numpy as np

from sciunit.base import SciUnit
from sciunit.utils import log, config_get
from sciunit.errors import InvalidScoreError
from typing import Union, Tuple

class Score(SciUnit):
    """Abstract base class for scores."""

    def __init__(self, score: 'Score', related_data: dict=None):
        """Abstract base class for scores.

        Args:
            score (int, float, bool): A raw value to wrap in a Score class.
            related_data (dict, optional): Artifacts to store with the score.
        """
        self.check_score(score)
        if related_data is None:
            related_data = {}
        self.score, self.related_data = score, related_data
        if isinstance(score, Exception):
            # Set to error score to use its summarize().
            self.__class__ = ErrorScore
        super(Score, self).__init__()

    score = None
    """The score itself."""

    _best = None
    """The best possible score of this type"""

    _worst = None
    """The best possible score of this type"""

    _allowed_types = None
    """List of allowed types for the score argument"""

    _allowed_types_message = ("Score of type %s is not an instance "
                              "of one of the allowed types: %s")
    """Error message when score argument is not one of these types"""

    _description = ""
    """A description of this score, i.e. how to interpret it.
    Provided in the score definition"""

    description = ""
    """A description of this score, i.e. how to interpret it.
    For the user to set in bind_score"""

    _raw = None
    """A raw number arising in a test's compute_score,
    used to determine this score. Can be set for reporting a raw value
    determined in Test.compute_score before any transformation,
    e.g. by a Converter"""

    related_data = None
    """Data specific to the result of a test run on a model."""

    test = None
    """The test taken. Set automatically by Test.judge."""

    model = None
    """The model judged. Set automatically by Test.judge."""

    def check_score(self, score: 'Score') -> None:
        """[summary]

        Args:
            score (Score): [description]

        Raises:
            InvalidScoreError: [description]
        """
        if self._allowed_types and \
          not isinstance(score, self._allowed_types+(Exception,)):
            raise InvalidScoreError(self._allowed_types_message %
                                    (type(score), self._allowed_types))
        self._check_score(score)

    def _check_score(self, score: 'Score') -> None:
        """A method for each Score subclass to impose additional constraints on the score, e.g. the range of the allowed score

        Args:
            score (Score): [description]
        """
        pass

    @classmethod
    def compute(cls, observation: dict, prediction: dict):
        """Compute whether the observation equals the prediction.

        Args:
            observation (dict): [description]
            prediction (dict): [description]

        Returns:
            [type]: [description]
        """
        return NotImplementedError("")
    
    @property
    def norm_score(self) -> 'Score':
        """A floating point version of the score used for sorting.
        If normalized = True, this must be in the range 0.0 to 1.0,
        where larger is better (used for sorting and coloring tables).

        Returns:
            Score: [description]
        """
        return self.score
    
    @property
    def log_norm_score(self) -> np.ndarray:
        """The natural logarithm of the `norm_score`.
        This is useful for guaranteeing convexity in an error surface

        Returns:
            np.ndarray: [description]
        """
        return np.log(self.norm_score) if self.norm_score is not None else None
    
    @property
    def log2_norm_score(self) -> np.ndarray:
        """The logarithm base 2 of the `norm_score`.
        This is useful for guaranteeing convexity in an error surface

        Returns:
            np.ndarray: [description]
        """
        return np.log2(self.norm_score) if self.norm_score is not None else None
    
    @property
    def log10_norm_score(self) -> np.ndarray:
        """The logarithm base 10 of the `norm_score`.
        This is useful for guaranteeing convexity in an error surface

        Returns:
            np.ndarray: [description]
        """
        return np.log10(self.norm_score) if self.norm_score is not None else None

    def color(self, value: Union[float, 'Score']=None) -> tuple:
        """Turn the score intp an RGB color tuple of three 8-bit integers.

        Args:
            value (Union[float,, optional): [description]. Defaults to None.

        Returns:
            tuple: [description]
        """
        if value is None:
            value = self.norm_score
        rgb = Score.value_color(value)
        return rgb

    @classmethod
    def value_color(cls, value: Union[float, 'Score']) -> tuple:
        """[summary]

        Args:
            value (Union[float,): [description]

        Returns:
            tuple: [description]
        """
        import matplotlib.cm as cm
        if value is None or np.isnan(value):
            rgb = (128, 128, 128)
        else:
            cmap_low = config_get('cmap_low', 38)
            cmap_high = config_get('cmap_high', 218)
            cmap_range = cmap_high - cmap_low
            cmap = cm.RdYlGn(int(cmap_range*value+cmap_low))[:3]
            rgb = tuple([x*256 for x in cmap])
        return rgb

    @property
    def summary(self) -> str:
        """Summarize the performance of a model on a test.

        Returns:
            str: [description]
        """
        return "=== Model %s achieved score %s on test '%s'. ===" % \
               (str(self.model), str(self), self.test)

    def summarize(self):
        """[summary]
        """
        if self.score is not None:
            log("%s" % self.summary)

    def _describe(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        result = "No description available"
        if self.score is not None:
            if self.description:
                result = "%s" % self.description
            elif self.test.score_type.__doc__:
                result = self.describe_from_docstring()
        return result

    def describe_from_docstring(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        s = [self.test.score_type.__doc__.strip().
             replace('\n', '').replace('    ', '')]
        if self.test.converter:
            s += [self.test.converter.description]
        s += [self._description]
        result = '\n'.join(s)
        return result

    def describe(self, quiet: bool=False) -> Union[str, None]:
        """[summary]

        Args:
            quiet (bool, optional): [description]. Defaults to False.

        Returns:
            Union[str, None]: [description]
        """
        d = self._describe()
        if quiet:
            return d
        else:
            log(d)

    @property
    def raw(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        value = self._raw if self._raw else self.score
        if isinstance(value, (float, np.ndarray)):
            string = '%.4g' % value
            if hasattr(value, 'magnitude'):
                string += ' %s' % str(value.units)[4:]
        else:
            string = None
        return string

    def get_raw(self) -> float:
        """[summary]

        Returns:
            float: [description]
        """
        value = copy(self._raw) if self._raw else copy(self.score)
        return value

    def set_raw(self, raw: float) -> None:
        """[summary]

        Args:
            raw (float): [description]
        """
        self._raw = raw

    def __repr__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return self.__str__()

    def __str__(self) -> str:
        """[summary]

        Returns:
            str: [description]
        """
        return '%s' % self.score

    def __eq__(self, other: Union['Score', float]) -> bool:
        """[summary]

        Args:
            other (Union[): [description]

        Returns:
            bool: [description]
        """
        if isinstance(other, Score):
            result = self.norm_score == other.norm_score
        else:
            result = self.score == other
        return result

    def __ne__(self, other: Union['Score', float]) -> bool:
        """[summary]

        Args:
            other (Union[): [description]

        Returns:
            bool: [description]
        """
        if isinstance(other, Score):
            result = self.norm_score != other.norm_score
        else:
            result = self.score != other
        return result

    def __gt__(self, other: Union['Score', float]) -> bool:
        """[summary]

        Args:
            other (Union[): [description]

        Returns:
            bool: [description]
        """
        if isinstance(other, Score):
            result = self.norm_score > other.norm_score
        else:
            result = self.score > other
        return result

    def __ge__(self, other: Union['Score', float]) -> bool:
        """[summary]

        Args:
            other (Union[): [description]

        Returns:
            bool: [description]
        """
        if isinstance(other, Score):
            result = self.norm_score >= other.norm_score
        else:
            result = self.score >= other
        return result

    def __lt__(self, other: Union['Score', float]) -> bool:
        """[summary]

        Args:
            other (Union[): [description]

        Returns:
            bool: [description]
        """
        if isinstance(other, Score):
            result = self.norm_score < other.norm_score
        else:
            result = self.score < other
        return result

    def __le__(self, other: Union['Score', float]) -> bool:
        """[summary]

        Args:
            other (Union[): [description]

        Returns:
            bool: [description]
        """
        if isinstance(other, Score):
            result = self.norm_score <= other.norm_score
        else:
            result = self.score <= other
        return result

    @property
    def score_type(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self.__class__.__name__

    @classmethod
    def extract_means_or_values(cls, observation: dict, prediction: dict, key: str=None) -> Tuple[dict, dict]:
        """Extracts the mean, value, or user-provided key from the observation and prediction dictionaries.

        Args:
            observation (dict): [description]
            prediction (dict): [description]
            key (str, optional): [description]. Defaults to None.

        Returns:
            Tuple[dict, dict]: [description]
        """

        obs_mv = cls.extract_mean_or_value(observation, key)
        pred_mv = cls.extract_mean_or_value(prediction, key)
        return obs_mv, pred_mv

    @classmethod
    def extract_mean_or_value(cls, obs_or_pred: dict, key: str=None) -> float:
        """Extracts the mean, value, or user-provided key from an observation or prediction dictionary.

        Args:
            obs_or_pred (dict): [description]
            key (str, optional): [description]. Defaults to None.

        Raises:
            KeyError: [description]

        Returns:
            float: [description]
        """

        result = None
        if not isinstance(obs_or_pred, dict):
            result = obs_or_pred
        else:
            keys = ([key] if key is not None else []) + ['mean', 'value']
            for k in keys:
                if k in obs_or_pred:
                    result = obs_or_pred[k]
                    break
            if result is None:
                raise KeyError(("%s has neither a mean nor a single "
                                "value" % obs_or_pred))
        return result


class ErrorScore(Score):
    """A score returned when an error occurs during testing."""

    @property
    def norm_score(self) -> float:
        """[summary]

        Returns:
            float: [description]
        """
        return 0.0

    @property
    def summary(self) -> str:
        """Summarize the performance of a model on a test.

        Returns:
            str: [description]
        """
        return "== Model %s did not complete test %s due to error '%s'. ==" %\
               (str(self.model), str(self.test), str(self.score))

    def _describe(self) -> str:
        return self.summary

    def __str__(self) -> str:
        return 'Error'
