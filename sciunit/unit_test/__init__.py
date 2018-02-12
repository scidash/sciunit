"""Unit testing module for sciunit"""

import unittest

from .command_line_tests import *
from .config_tests import *
from .converter_tests import *
from .doc_tests import *
from .error_tests import *
from .model_tests import *
from .score_tests import *
from .test_tests import *
from .utils_tests import *

class ImportTestCase(unittest.TestCase):
    """Unit tests for imports"""

    def test_quantities(self):
        import quantities as pq
        pq.Quantity([10,20,30], pq.pA)


    def test_import_everything(self):
        import sciunit
        from sciunit.utils import import_all_modules
        
        # Recursively import all submodules
        import_all_modules(sciunit)
        