"""SciUnit.

A Testing Framework for Data-Driven Validation of
Quantitative Scientific Models
"""

from .utils import RUNTIME_SETTINGS, log, config_set, config_get
from .models import Model
from .capabilities import Capability
from .tests import Test, TestM2M
from .suites import TestSuite
from .scores import Score
from .errors import Error
from .scores.collections import ScoreArray, ScoreMatrix#, ScorePanel
from .scores.collections_m2m import ScoreArrayM2M, ScoreMatrixM2M

from importlib.metadata import version
__version__ = version('sciunit')

import logging
logger = logging.getLogger("sciunit")
logger.setLevel(logging.WARNING)
