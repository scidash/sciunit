"""SciUnit.

A Testing Framework for Data-Driven Validation of
Quantitative Scientific Models
"""

import json
import logging
import sys

from .base import config, __version__, logger, log
from .capabilities import Capability
from .errors import Error
from .models import Model
from .models.backends import Backend
from .scores import Score
from .scores.collections import ScoreArray, ScoreMatrix
from .scores.collections_m2m import ScoreArrayM2M, ScoreMatrixM2M
from .suites import TestSuite
from .tests import Test, TestM2M
