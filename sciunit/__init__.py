"""SciUnit.

A Testing Framework for Data-Driven Validation of
Quantitative Scientific Models
"""

from importlib.metadata import version

from .capabilities import Capability
from .errors import Error
from .models import Model
from .scores import Score
from .scores.collections import ScoreArray, ScoreMatrix  # , ScorePanel
from .scores.collections_m2m import ScoreArrayM2M, ScoreMatrixM2M
from .suites import TestSuite
from .tests import Test, TestM2M
from .utils import RUNTIME_SETTINGS, config_get, config_set, log

__version__ = version('sciunit')

import logging

logger = logging.getLogger("sciunit")
logger.setLevel(logging.WARNING)
