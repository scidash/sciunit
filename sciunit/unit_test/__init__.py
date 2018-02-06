"""All unit tests for SciUnit"""

import unittest
import sys

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
        import quantities

    def test_import_everything(self):
        import sciunit
        from sciunit.utils import import_all_modules
        
        # Recursively import all submodules
        import_all_modules(sciunit)
        

if __name__ == '__main__':
    buffer = 'buffer' in sys.argv
    sys.argv = sys.argv[:1] # Args need to be removed for __main__ to work.  
    unittest.main(buffer=buffer)
