"""Unit tests for (sciunit) tests and test suites"""

import unittest

from sciunit import TestSuite
from sciunit.tests import RangeTest, TestM2M
from sciunit.models.examples import ConstModel, UniformModel
from sciunit.scores import BooleanScore, FloatScore
from sciunit.scores import FloatScore
from sciunit.capabilities import ProducesNumber

from sciunit.unit_test.base import SuiteBase

class TestsTestCase(unittest.TestCase):
    """Unit tests for the sciunit module"""

    def setUp(self):
        self.M = UniformModel
        self.T = RangeTest

    def test_get_test_description(self):
        t = self.T([2, 3])
        t.describe()
        t.description = "Lorem Ipsum"
        t.describe()

        class MyTest(self.T):
            """Lorem Ipsum"""
            pass

        t = MyTest([2, 3])
        t.description = None
        self.assertEqual(t.describe(),"Lorem Ipsum")

    def test_check_model_capabilities(self):
        t = self.T([2, 3])
        m = self.M(2, 3)
        t.check(m)

    def test_rangetest(self):
        range_2_3_test = RangeTest(observation=[2, 3])
        one_model = ConstModel(2.5)
        self.assertTrue(range_2_3_test.check_capabilities(one_model))
        score = range_2_3_test.judge(one_model)
        self.assertTrue(isinstance(score, BooleanScore))
        self.assertEqual(score.score,True)
        self.assertTrue(score.test is range_2_3_test)
        self.assertTrue(score.model is one_model)


class TestSuitesTestCase(SuiteBase,unittest.TestCase):
    """Unit tests for the sciunit module"""

    def test_testsuite(self):
        t1 = self.T([2,3])
        t2 = self.T([5,6])
        m1 = self.M(2,3)
        m2 = self.M(5,6)
        t = TestSuite([t1,t2])
        t.judge([m1,m2])
        t = TestSuite([t1,t2],skip_models=[m1],include_models=[m2])
        t.judge([m1,m2])

    def test_testsuite_hooks(self):
        t1 = self.T([2,3])
        t1.hook_called = False
        t2 = self.T([5,6])
        m = self.M(2,3)
        def f(test, tests, score, a=None):
            self.assertEqual(score,True)
            self.assertEqual(a,1)
            t1.hook_called = True
        ts = TestSuite([t1,t2],name='MySuite',
                      hooks={t1:
                                {'f':f,
                                 'kwargs':{'a':1}}
                            })
        ts.judge(m)
        self.assertEqual(t1.hook_called,True)

    def test_testsuite_from_observations(self):
        m = self.M(2,3)
        ts = TestSuite.from_observations([(self.T,[2,3]),
                                         (self.T,[5,6])],
                                        name="MySuite")
        ts.judge(m)

    def test_testsuite_set_verbose(self):
        t1 = self.T([2,3])
        t2 = self.T([5,6])
        t = TestSuite([t1,t2])
        t.set_verbose(True)
        self.assertEqual(t1.verbose,True)
        self.assertEqual(t2.verbose,True)

    def test_testsuite_serialize(self):
        tests = [RangeTest(observation=(x,x+3)) for x in [1,2,3,4]]
        ts = TestSuite(tests, name='RangeSuite')
        self.assertTrue(isinstance(ts.json(),str))


class M2MsTestCase(unittest.TestCase):
    """Tests for the M2M flavor of tests and test suites"""

    def setUp(self):
        self.myModel1 = ConstModel(100.0, "Model1")
        self.myModel2 = ConstModel(110.0, "Model2")

        class NumberTest_M2M(TestM2M):
            """Dummy Test"""
            score_type = FloatScore
            description = ("Tests the parameter 'value' between two models")

            def __init__(self, observation=None, name="ValueTest-M2M"):
                TestM2M.__init__(self,observation,name)
                self.required_capabilities += (ProducesNumber,)

            def generate_prediction(self, model, verbose=False):
                """Implementation of sciunit.Test.generate_prediction."""
                prediction = model.produce_number()
                return prediction

            def compute_score(self, prediction1, prediction2):
                """Implementation of sciunit.Test.score_prediction."""
                score = FloatScore(prediction1 - prediction2)
                score.description = "Difference between model predictions"
                return score

        self.NumberTest_M2M = NumberTest_M2M

    def test_testm2m_with_observation(self):
        myTest = self.NumberTest_M2M(observation=95.0)
        myScore = myTest.judge([self.myModel1, self.myModel2])

        # Test model vs observation
        self.assertEqual(myScore[myTest][self.myModel1], -5.0)
        self.assertEqual(myScore[self.myModel1][myTest], 5.0)
        self.assertEqual(myScore["observation"][self.myModel2], -15.0)
        self.assertEqual(myScore[self.myModel2]["observation"], 15.0)

        # Test model vs model
        self.assertEqual(myScore[self.myModel1][self.myModel2], -10.0)
        self.assertEqual(myScore[self.myModel2][self.myModel1], 10.0)

    def test_testm2m_without_observation(self):
        myTest = self.NumberTest_M2M(observation=None)
        myScore = myTest.judge([self.myModel1, self.myModel2])

        # Test model vs model; different ways of specifying individual scores
        self.assertEqual(myScore[self.myModel1][self.myModel2], -10.0)
        self.assertEqual(myScore[self.myModel2][self.myModel1], 10.0)
        self.assertEqual(myScore["Model1"][self.myModel2], -10.0)
        self.assertEqual(myScore["Model2"][self.myModel1], 10.0)
        self.assertEqual(myScore[self.myModel1][self.myModel1], 0.0)
        self.assertEqual(myScore["Model2"]["Model2"], 0.0)
