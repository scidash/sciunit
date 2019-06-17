"""Abstract base class from some SciUnit unit test cases"""

from sciunit import TestSuite
from sciunit.tests import RangeTest
from sciunit.models.examples import UniformModel


class SuiteBase(object):
    """Abstract base class for testing suites and scores"""

    def setUp(self):
        self.M = UniformModel
        self.T = RangeTest

    def prep_models_and_tests(self):
        t1 = self.T([2, 3], name='test1')
        t2 = self.T([5, 6])
        m1 = self.M(2, 3)
        m2 = self.M(5, 6)
        ts = TestSuite([t1, t2], name="MySuite")
        return (ts, t1, t2, m1, m2)
