"""SciUnit.

A Testing Framework for Data-Driven Validation of
Quantitative Scientific Models
"""

from __future__ import print_function
from __future__ import unicode_literals

from .utils import settings, log
from .models import Model
from .capabilities import Capability
from .tests import Test, TestM2M
from .suites import TestSuite
from .scores import Score
from .errors import Error
from .scores.collections import ScoreArray, ScoreMatrix, ScorePanel
from .scores.collections_m2m import ScoreArrayM2M, ScoreMatrixM2M
from .version import __version__
