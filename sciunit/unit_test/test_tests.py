"""Unit tests for (sciunit) tests and test suites"""

import unittest

from sciunit import TestSuite, Model, config_set
from sciunit.tests import RangeTest, TestM2M, Test, ProtocolToFeaturesTest
from sciunit.models.examples import ConstModel, UniformModel
from sciunit.scores import BooleanScore, FloatScore
from sciunit.scores.collections import ScoreMatrix
from sciunit.capabilities import ProducesNumber
from sciunit.errors import ObservationError, ParametersError, Error, InvalidScoreError
from .base import SuiteBase


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
        self.assertEqual(t.describe(), "Lorem Ipsum")

    def test_check_model_capabilities(self):
        t = self.T([2, 3])
        m = self.M(2, 3)
        t.check(m)

    def test_rangetest(self):
        from sciunit.converters import NoConversion

        range_2_3_test = RangeTest(observation=[2, 3])
        range_2_3_test.converter = NoConversion()
        one_model = ConstModel(2.5)
        self.assertTrue(range_2_3_test.check_capabilities(one_model))
        score = range_2_3_test.judge(one_model)
        self.assertTrue(isinstance(score, BooleanScore))
        self.assertEqual(score.score, True)
        self.assertTrue(score.test is range_2_3_test)
        self.assertTrue(score.model is one_model)

    def test_Test(self):
        config_set('PREVALIDATE', True)
        with self.assertRaises(ObservationError):
            t = Test(None)
        config_set('PREVALIDATE', False)

        t = Test(None)
        self.assertRaises(ObservationError, t.validate_observation, None)
        self.assertRaises(
            ObservationError, t.validate_observation, "I am not an observation"
        )
        self.assertRaises(ObservationError, t.validate_observation, {"mean": None})
        t = Test([0, 1])
        t.observation_schema = {}
        t.validate_observation({0: 0, 1: 1})
        Test.observation_schema = [{}, {}]
        self.assertListEqual(t.observation_schema_names(), ["Schema 1", "Schema 2"])

        self.assertRaises(ParametersError, t.validate_params, None)
        self.assertRaises(ParametersError, t.validate_params, "I am not an observation")
        t.params_schema = {}
        t.validate_params({0: 1, 1: 2})

        self.assertRaises(Error, t.check_capabilities, "I am not a model")
        t.condition_model(Model())
        self.assertRaises(NotImplementedError, t.generate_prediction, Model())
        self.assertRaises(NotImplementedError, t.optimize, Model())

        self.assertTrue(t.compute_score({0: 2, 1: 2}, {0: 2, 1: 2}).score)
        self.assertFalse(t.compute_score({0: -2, 1: 2}, {0: 2, 1: -2}).score)
        t.score_type = None
        self.assertRaises(NotImplementedError, t.compute_score, {}, {})

        t.score_type = BooleanScore
        self.assertRaises(InvalidScoreError, t.check_score_type, FloatScore(0.5))
        self.assertRaises(ObservationError, t.judge, [Model(), Model()])


class TestSuitesTestCase(SuiteBase, unittest.TestCase):
    """Unit tests for the sciunit module"""

    def test_testsuite(self):
        t1 = self.T([2, 3])
        t2 = self.T([5, 6])
        m1 = self.M(2, 3)
        m2 = self.M(5, 6)
        t = TestSuite([t1, t2])
        t.judge([m1, m2])
        self.assertIsInstance(t.check([m1, m2]), ScoreMatrix)
        capa_list = t.check_capabilities(m1)
        self.assertTrue(capa_list[0])
        self.assertTrue(capa_list[1])

        t = TestSuite(
            {"test 1": t1, "test 2": t2, "test 3 (non-Test)": "I am not a Test"}
        )
        self.assertRaises(TypeError, t.assert_tests, 0)
        self.assertRaises(TypeError, t.assert_tests, [0])
        self.assertRaises(TypeError, t.assert_models, 0)
        self.assertRaises(TypeError, t.assert_models, [0])
        self.assertRaises(NotImplementedError, t.optimize, m1)
        self.assertRaises(KeyError, t.__getitem__, "wrong name")
        self.assertIsInstance(t[0], RangeTest)

        t.judge([m1, m2])
        t = TestSuite([t1, t2], skip_models=[m1], include_models=[m2])
        t.judge([m1, m2])

    def test_testsuite_hooks(self):
        t1 = self.T([2, 3])
        t1.hook_called = False
        t2 = self.T([5, 6])
        m = self.M(2, 3)

        def f(test, tests, score, a=None):
            self.assertEqual(score, True)
            self.assertEqual(a, 1)
            t1.hook_called = True

        ts = TestSuite(
            [t1, t2], name="MySuite", hooks={t1: {"f": f, "kwargs": {"a": 1}}}
        )
        ts.judge(m)
        self.assertEqual(t1.hook_called, True)

    def test_testsuite_from_observations(self):
        m = self.M(2, 3)
        ts = TestSuite.from_observations(
            [(self.T, [2, 3]), (self.T, [5, 6])], name="MySuite"
        )
        ts.judge(m)

    def test_testsuite_set_verbose(self):
        t1 = self.T([2, 3])
        t2 = self.T([5, 6])
        t = TestSuite([t1, t2])
        t.set_verbose(True)
        self.assertEqual(t1.verbose, True)
        self.assertEqual(t2.verbose, True)

    def test_testsuite_serialize(self):
        tests = [RangeTest(observation=(x, x + 3)) for x in [1, 2, 3, 4]]
        ts = TestSuite(tests, name="RangeSuite")
        self.assertTrue(isinstance(ts.json(), str))


class M2MsTestCase(unittest.TestCase):
    """Tests for the M2M flavor of tests and test suites"""

    def setUp(self):
        self.myModel1 = ConstModel(100.0, "Model1")
        self.myModel2 = ConstModel(110.0, "Model2")

        class NumberTest_M2M(TestM2M):
            """Dummy Test"""

            score_type = FloatScore
            description = "Tests the parameter 'value' between two models"

            def __init__(self, observation=None, name="ValueTest-M2M"):
                TestM2M.__init__(self, observation, name)
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

    def test_testm2m(self):
        myTest = TestM2M(observation=95.0)
        myTest.validate_observation(None)
        myTest.score_type = None
        self.assertRaises(NotImplementedError, myTest.compute_score, {}, {})
        myTest.score_type = BooleanScore
        self.assertTrue(myTest.compute_score(95, 96))
        self.assertRaises(TypeError, myTest.judge, "str")


class ProtocolToFeaturesTestCase(unittest.TestCase):
    def test_ProtocolToFeaturesTest(self):
        t = ProtocolToFeaturesTest([1, 2, 3])
        m = Model()
        m.run = lambda: 0

        self.assertIsInstance(t.generate_prediction(m), NotImplementedError)
        self.assertIsInstance(t.setup_protocol(m), NotImplementedError)
        self.assertIsInstance(t.get_result(m), NotImplementedError)
        self.assertIsInstance(t.extract_features(m, list()), NotImplementedError)


if __name__ == "__main__":
    unittest.main()
