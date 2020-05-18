"""All unit tests for SciUnit"""

import sys
import unittest
#from active import * # Import all the tests from the unit_test.active module

from backend_tests import *
#from command_line_tests import *
from config_tests import *
from converter_tests import *
from doc_tests import *
from error_tests import *
#from import_tests import *
from observation_tests import *
from model_tests import *
from score_tests import *
from test_tests import *
from utils_tests import *
#def main():
#    buffer = 'buffer' in sys.argv
#    sys.argv = sys.argv[:1] # :Args need to be removed for __main__ to work.  
#    unittest.main(buffer=buffer)
#
#if __name__ == '__main__':
#    main()

unittest.main()
    