"""Common imports for many unit tests in this directory"""

import matplotlib as mpl
import sys
import unittest

OSX = sys.platform == 'darwin'
if OSX or 'Qt' in mpl.rcParams['backend']:
    mpl.use('Agg')  # Avoid any problems with Macs or headless displays.

class SuiteBase(object):
    """Abstract base class for testing suites and scores"""

    def setUp(self):
        from sciunit.models.examples import UniformModel
        from sciunit.tests import RangeTest
        self.M = UniformModel
        self.T = RangeTest

    def prep_models_and_tests(self):
        from sciunit import TestSuite
        t1 = self.T([2, 3], name='test1')
        t2 = self.T([5, 6])
        m1 = self.M(2, 3)
        m2 = self.M(5, 6)
        ts = TestSuite([t1, t2], name="MySuite")
        return (ts, t1, t2, m1, m2)
