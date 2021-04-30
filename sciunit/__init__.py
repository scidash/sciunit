"""SciUnit.

A Testing Framework for Data-Driven Validation of
Quantitative Scientific Models
"""

import logging
import sys

from .capabilities import Capability
from .errors import Error
from .models import Model
from .scores import Score
from .scores.collections import ScoreArray, ScoreMatrix
from .scores.collections_m2m import ScoreArrayM2M, ScoreMatrixM2M
from .suites import TestSuite
from .tests import Test, TestM2M
from .utils import RUNTIME_SETTINGS, config_get, config_set, log


try:
    from importlib.metadata import version
    __version__ = version("sciunit")
except:
    __version__ = None
    
logger = logging.getLogger("sciunit")
logger.setLevel(logging.WARNING)
