"""Unit tests for SciUnit"""

# Run with any of:
# python test_all.py
# python -m unittest test_all.py

# coverage run --source . test_all.py

import os
import platform
import unittest
import tempfile

import numpy as np
from IPython.display import display

from sciunit.utils import NotebookTools, import_all_modules


class DocumentationTestCase(NotebookTools,unittest.TestCase):
    """Unit tests for documentation notebooks"""

    path = '../../docs'

    def test_chapter1(self):
        self.do_notebook('chapter1')

    def test_chapter2(self):
        self.do_notebook('chapter2')

    def test_chapter3(self):
        self.do_notebook('chapter3')


class ImportTestCase(unittest.TestCase):
    """Unit tests for imports"""

    def test_quantities(self):
        import quantities

    def test_import_everything(self):
        import sciunit

        # Recursively import all submodules
        import_all_modules(sciunit)


class InitTestCase(unittest.TestCase):
    """Unit tests for the sciunit module"""

    def setUp(self):
        from sciunit.tests.example import RangeTest
        from sciunit.models import UniformModel
        self.M = UniformModel
        self.T = RangeTest

    def test_log(self):
        from sciunit import log

        log("Lorem Ipsum")

    def test_get_model_state(self):
        from sciunit import Model

        m = Model()
        state = m.__getstate__()
        self.assertEqual(m.__dict__,state)

    def test_get_model_capabilities(self):
        from sciunit.capabilities import ProducesNumber

        m = self.M(2,3)
        self.assertEqual(m.capabilities,['ProducesNumber'])

    def test_get_model_description(self):
        from sciunit.models import UniformModel

        m = self.M(2,3)
        m.describe()
        m.description = "Lorem Ipsum"
        m.describe()

    def test_get_test_description(self):
        t = self.T([2,3])
        t.describe()
        t.description = "Lorem Ipsum"
        t.describe()

        class MyTest(self.T):
            """Lorem Ipsum"""
            pass

        t = MyTest([2,3])
        t.description = None
        self.assertEqual(t.describe(),"Lorem Ipsum")

    def test_check_model_capabilities(self):
        t = self.T([2,3])
        m = self.M(2,3)
        t.check(m)

    def test_testsuite(self):
        from sciunit import TestSuite

        t1 = self.T([2,3])
        t2 = self.T([5,6])
        m1 = self.M(2,3)
        m2 = self.M(5,6)
        t = TestSuite("MySuite",[t1,t2])
        t.judge([m1,m2])
        t = TestSuite("MySuite",[t1,t2],skip_models=[m1],include_models=[m2])
        t.judge([m1,m2])

    def test_testsuite_hooks(self):
        from sciunit import TestSuite

        t1 = self.T([2,3])
        t1.hook_called = False
        t2 = self.T([5,6])
        m = self.M(2,3)
        def f(test, tests, score, a=None):
            self.assertEqual(score,True)
            self.assertEqual(a,1)
            t1.hook_called = True
        t = TestSuite("MySuite",[t1,t2],
                      hooks={t1:
                                {'f':f,
                                 'kwargs':{'a':1}}
                            })
        t.judge(m)
        self.assertEqual(t1.hook_called,True)

    def test_testsuite_from_observations(self):
        from sciunit import TestSuite

        m = self.M(2,3)
        t = TestSuite.from_observations("MySuite",
                                        [(self.T,[2,3]),
                                         (self.T,[5,6])])
        t.judge(m)


    def test_testsuite_set_verbose(self):
        from sciunit import TestSuite

        t1 = self.T([2,3])
        t2 = self.T([5,6])
        t = TestSuite("MySuite",[t1,t2])
        t.set_verbose(True)
        self.assertEqual(t1.verbose,True)
        self.assertEqual(t2.verbose,True)

    def prep_models_and_tests(self):
        from sciunit import TestSuite

        t1 = self.T([2,3],name='test1')
        t2 = self.T([5,6])
        m1 = self.M(2,3)
        m2 = self.M(5,6)
        t = TestSuite("MySuite",[t1,t2])
        return (t,t1,t2,m1,m2)

    def test_score_matrix(self):
        from sciunit import ScoreMatrix

        t,t1,t2,m1,m2 = self.prep_models_and_tests()
        sm = t.judge(m1)
        self.assertTrue(type(sm) is ScoreMatrix)
        self.assertTrue(sm[t1][m1].score)
        self.assertTrue(sm['test1'][m1].score)
        self.assertTrue(sm[m1]['test1'].score)
        self.assertFalse(sm[t2][m1].score)
        self.assertEqual(sm[(m1,t1)].score,True)
        self.assertEqual(sm[(m1,t2)].score,False)
        sm = t.judge([m1,m2])
        self.assertEqual(sm.stature(t1,m1),1)
        self.assertEqual(sm.stature(t1,m2),2)
        display(sm)

    def test_score_arrays(self):
        from sciunit import ScoreArray

        t,t1,t2,m1,m2 = self.prep_models_and_tests()
        sm = t.judge(m1)
        sa = sm[m1]
        self.assertTrue(type(sa) is ScoreArray)
        self.assertEqual(list(sa.sort_keys.values),[1.0,0.0])
        self.assertEqual(sa.stature(t1),1)
        self.assertEqual(sa.stature(t2),2)
        self.assertEqual(sa.stature(t1),1)
        display(sa)

    @unittest.skip("Currently failing because ScorePanel just stores sm1 twice")
    def test_score_panel(self):
        from sciunit import ScorePanel

        t,t1,t2,m1,m2 = self.prep_models_and_tests()
        sm1 = t.judge([m1,m2])
        sm2 = t.judge([m2,m1])
        sp = ScorePanel(data={1:sm1,2:sm2})
        self.assertTrue(sp[1].equals(sm1))
        self.assertTrue(sp[2].equals(sm2))

    def test_error_types(self):
        from sciunit import CapabilityError, BadParameterValueError,\
                            PredictionError, InvalidScoreError, \
                            Model, Capability

        CapabilityError(Model(),Capability)
        PredictionError(Model(),'foo')
        InvalidScoreError()
        BadParameterValueError('x',3)

    def test_testm2m_with_observation(self):
        import sciunit
        from sciunit.scores import FloatScore
        from sciunit.capabilities import ProducesNumber
        from sciunit.models import ConstModel

        class NumberTest_M2M(sciunit.TestM2M):
            """Dummy Test"""
            score_type = FloatScore
            description = ("Tests the parameter 'value' between two models")

            def __init__(self, observation=None, name="ValueTest-M2M"):
                sciunit.TestM2M.__init__(self,observation,name)
                self.required_capabilities += (ProducesNumber,)

            def generate_prediction(self, model, verbose=False):
                """Implementation of sciunit.Test.generate_prediction."""
                prediction = model.produce_number()
                return prediction

            def compute_score(self, prediction1, prediction2):
                """Implementation of sciunit.Test.score_prediction."""
                score = sciunit.scores.FloatScore(prediction1 - prediction2)
                score.description = "Difference between model predictions"
                return score

        myModel1 = ConstModel(100.0, "Model1")
        myModel2 = ConstModel(110.0, "Model2")
        myTest = NumberTest_M2M(observation=95.0)
        myScore = myTest.judge([myModel1, myModel2])

        # Test model vs observation
        self.assertEqual(myScore[myTest][myModel1], -5.0)
        self.assertEqual(myScore[myModel1][myTest], 5.0)
        self.assertEqual(myScore["observation"][myModel2], -15.0)
        self.assertEqual(myScore[myModel2]["observation"], 15.0)

        # Test model vs model
        self.assertEqual(myScore[myModel1][myModel2], -10.0)
        self.assertEqual(myScore[myModel2][myModel1], 10.0)

    def test_testm2m_without_observation(self):
        import sciunit
        from sciunit.scores import FloatScore
        from sciunit.capabilities import ProducesNumber
        from sciunit.models import ConstModel

        class NumberTest_M2M(sciunit.TestM2M):
            """Dummy Test"""
            score_type = FloatScore
            description = ("Tests the parameter 'value' between two models")

            def __init__(self, observation=None, name="ValueTest-M2M"):
                sciunit.TestM2M.__init__(self,observation,name)
                self.required_capabilities += (ProducesNumber,)

            def generate_prediction(self, model, verbose=False):
                """Implementation of sciunit.Test.generate_prediction."""
                prediction = model.produce_number()
                return prediction

            def compute_score(self, prediction1, prediction2):
                """Implementation of sciunit.Test.score_prediction."""
                score = sciunit.scores.FloatScore(prediction1 - prediction2)
                score.description = "Difference between model predictions"
                return score

        myModel1 = ConstModel(100.0, "Model1")
        myModel2 = ConstModel(110.0, "Model2")
        myTest = NumberTest_M2M(observation=95.0)
        myScore = myTest.judge([myModel1, myModel2])

        # Test model vs observation; different ways of specifying individual scores
        self.assertEqual(myScore[myTest][myModel1], -5.0)
        self.assertEqual(myScore[myModel1][myTest], 5.0)
        self.assertEqual(myScore["observation"][myModel2], -15.0)
        self.assertEqual(myScore[myModel2]["observation"], 15.0)
        self.assertEqual(myScore[myTest][myTest], 0.0)
        self.assertEqual(myScore["observation"]["observation"], 0.0)

        # Test model vs model; different ways of specifying individual scores
        self.assertEqual(myScore[myModel1][myModel2], -10.0)
        self.assertEqual(myScore[myModel2][myModel1], 10.0)
        self.assertEqual(myScore["Model1"][myModel2], -10.0)
        self.assertEqual(myScore["Model2"][myModel1], 10.0)
        self.assertEqual(myScore[myModel1][myModel1], 0.0)
        self.assertEqual(myScore["Model2"]["Model2"], 0.0)

class CapabilitiesTestCase(unittest.TestCase):
    """Unit tests for sciunit Capability classes"""

    def test_capabilities(self):
        from sciunit import Model
        from sciunit.capabilities import ProducesNumber,UniqueRandomNumberModel,\
                                         RepeatedRandomNumberModel

        class MyModel(Model,ProducesNumber):
            def produce_number(self):
                return 3.14
        m = MyModel()
        self.assertEqual(m.produce_number(),3.14)

        m = UniqueRandomNumberModel()
        self.assertNotEqual(m.produce_number(),m.produce_number())

        m = RepeatedRandomNumberModel()
        self.assertEqual(m.produce_number(),m.produce_number())


class ModelsTestCase(unittest.TestCase):
    """Unit tests for sciunit Model classes"""

    def test_regular_models(self):
        from sciunit.models import ConstModel,UniformModel,SharedModel

        m = ConstModel(3)
        self.assertEqual(m.produce_number(),3)

        m = UniformModel(3,4)
        self.assertTrue(3 < m.produce_number() < 4)

    def test_irregular_models(self):
        from sciunit.models import CacheByInstancePersistentUniformModel,\
                                   CacheByValuePersistentUniformModel

        a = CacheByInstancePersistentUniformModel(2,3)
        a1 = a.produce_number()
        a2 = a.produce_number()
        self.assertEqual(a1,a2)
        b = CacheByInstancePersistentUniformModel(2,3)
        b1 = b.produce_number()
        self.assertNotEqual(b1,a2)

        c = CacheByValuePersistentUniformModel(2,3)
        c1 = c.produce_number()
        c2 = c.produce_number()
        self.assertEqual(c1,c2)
        d = CacheByValuePersistentUniformModel(2,3)
        d1 = d.produce_number()
        self.assertEqual(d1,c2)


class ScoresTestCase(unittest.TestCase):
    """Unit tests for sciunit Score classes"""

    def test_regular_score_types(self):
        from sciunit.scores import BooleanScore,FloatScore,RatioScore,\
                                   ZScore,CohenDScore,PercentScore
        from sciunit.tests.example import RangeTest

        BooleanScore(True)
        BooleanScore(False)
        score = BooleanScore.compute(5,5)
        self.assertEqual(score.sort_key,1)
        score = BooleanScore.compute(4,5)
        self.assertEqual(score.sort_key,0)

        t = RangeTest([2,3])
        score.test = t
        score.describe()
        score.description = "Lorem Ipsum"
        score.describe()

        score = FloatScore(3.14)
        obs = np.array([1.0,2.0,3.0])
        pred = np.array([1.0,2.0,4.0])
        score = FloatScore.compute_ssd(obs,pred)
        self.assertEqual(score.score,1.0)

        RatioScore(1.2)
        score = RatioScore.compute({'mean':4.,'std':1.},{'value':2.})
        self.assertEqual(score.score,0.5)

        score = PercentScore(42)
        self.assertEqual(score.sort_key,0.42)

        ZScore(0.7)
        score = ZScore.compute({'mean':3.,'std':1.},{'value':2.})
        self.assertEqual(score.score,-1.)

        CohenDScore(-0.3)
        score = CohenDScore.compute({'mean':3.,'std':1.},{'mean':2.,'std':1.})
        self.assertTrue(-0.708 < score.score < -0.707)

    def test_irregular_score_types(self):
        from sciunit import ErrorScore,NAScore,TBDScore,NoneScore
        from sciunit.scores import InsufficientDataScore

        e = Exception("This is an error")
        score = ErrorScore(e)
        score = NAScore(None)
        score = TBDScore(None)
        score = NoneScore(None)
        score = InsufficientDataScore(None)
        self.assertEqual(score.sort_key,None)


class ConvertersTestCase(unittest.TestCase):
    """Unit tests for Score converters"""

    def test_converters(self):
        from sciunit.converters import NoConversion,LambdaConversion,\
                                       AtMostToBoolean,AtLeastToBoolean,\
                                       RangeToBoolean
        from sciunit.scores import BooleanScore,ZScore

        old_score = ZScore(1.3)
        new_score = NoConversion().convert(old_score)
        self.assertEqual(old_score,new_score)
        new_score = LambdaConversion(lambda x:x.score**2).convert(old_score)
        self.assertEqual(old_score.score**2,new_score.score)
        new_score = AtMostToBoolean(3).convert(old_score)
        self.assertEqual(new_score,BooleanScore(True))
        new_score = AtMostToBoolean(1).convert(old_score)
        self.assertEqual(new_score,BooleanScore(False))
        new_score = AtLeastToBoolean(1).convert(old_score)
        self.assertEqual(new_score,BooleanScore(True))
        new_score = AtLeastToBoolean(3).convert(old_score)
        self.assertEqual(new_score,BooleanScore(False))
        new_score = RangeToBoolean(1,3).convert(old_score)
        self.assertEqual(new_score,BooleanScore(True))
        new_score = RangeToBoolean(3,5).convert(old_score)
        self.assertEqual(new_score,BooleanScore(False))
        self.assertEqual(new_score.raw,str(old_score.score))


class UtilsTestCase(unittest.TestCase):
    """Unit tests for sciunit.utils"""

    def test_assert_dimensionless(self):
        import quantities as pq
        from sciunit.utils import assert_dimensionless

        assert_dimensionless(3*pq.s*pq.Hz)
        try:
            assert_dimensionless(3*pq.s)
        except TypeError:
            pass
        else:
            raise Exception("Should have produced a type error")

    def test_printd(self):
        from sciunit.utils import printd, printd_set

        printd_set(True)
        self.assertTrue(printd("This line should print"))
        printd_set(False)
        self.assertFalse(printd("This line should not print"))

    def test_dict_hash(self):
        from sciunit.utils import dict_hash

        d1 = {'a':1,'b':2,'c':3}
        d2 = {'c':3,'a':1,'b':2}
        dh1 = dict_hash(d1)
        dh2 = dict_hash(d2)
        self.assertTrue(type(dh1) is str)
        self.assertTrue(type(dh2) is str)
        self.assertEqual(d1,d2)


class CommandLineTestCase(unittest.TestCase):
    """Unit tests for command line tools"""

    def setUp(self):
        from sciunit.__main__ import main
        import sciunit

        self.main = main
        SCIDASH_HOME = os.path.dirname(os.path.dirname(sciunit.__path__[0]))
        self.cosmosuite_path = os.path.join(SCIDASH_HOME,'scidash')

    def test_sciunit_1create(self):
        try:
            self.main('--directory',self.cosmosuite_path,'create')
        except Exception as e:
            if 'There is already a configuration file' not in str(e):
                raise e
            else:
                temp_path = tempfile.mkdtemp()
                self.main('--directory',temp_path,'create')

    def test_sciunit_2check(self):
        self.main('--directory',self.cosmosuite_path,'check')

    def test_sciunit_3run(self):
        self.main('--directory',self.cosmosuite_path,'run')

    def test_sciunit_4make_nb(self):
        self.main('--directory',self.cosmosuite_path,'make-nb')

    # Skip for python versions that don't have importlib.machinery
    @unittest.skipIf(platform.python_version()<'3.3',
                     "run-nb not supported on Python < 3.3")
    def test_sciunit_5run_nb(self):
        self.main('--directory',self.cosmosuite_path,'run-nb')


class ExampleTestCase(unittest.TestCase):
    """Unit tests for example modules"""

    def test_example1(self):
        from sciunit.tests import example


if __name__ == '__main__':
    unittest.main()
