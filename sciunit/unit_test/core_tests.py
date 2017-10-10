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

    def test_log(self):
        from sciunit import log
        
        log("Lorem Ipsum")

    def test_get_model_state(self):
        from sciunit import Model
        
        m = Model()
        state = m.__getstate__()
        self.assertEqual(m.__dict__,state)

    def test_get_model_capabilities(self):
        from sciunit.models import UniformModel
        from sciunit.capabilities import ProducesNumber
        
        m = UniformModel(2,3)
        self.assertEqual(m.capabilities,['ProducesNumber'])

    def test_get_model_description(self):
        from sciunit.models import UniformModel
        
        m = UniformModel(2,3)
        m.describe()
        m.description = "Lorem Ipsum"
        m.describe()

    def test_get_test_description(self):
        from sciunit.tests.example import PositivityTest
        
        t = PositivityTest()
        t.describe()
        t.description = "Lorem Ipsum"
        t.describe()

        class MyTest(PositivityTest):
            """Lorem Ipsum"""
            pass
        t = MyTest()
        t.description = None
        self.assertEqual(t.describe(),"Lorem Ipsum")

    def test_check_model_capabilities(self):
        from sciunit.tests.example import PositivityTest
        from sciunit.models import UniformModel

        t = PositivityTest()
        m = UniformModel(2,3)
        t.check(m)

    def test_testsuite(self):
        from sciunit import TestSuite
        from sciunit.tests.example import PositivityTest
        from sciunit.models import UniformModel
        t1 = PositivityTest()
        t2 = PositivityTest()
        m1 = UniformModel(2,3)
        m2 = UniformModel(5,6)
        t = TestSuite("MySuite",[t1,t2])
        t.judge([m1,m2])
        t = TestSuite("MySuite",[t1,t2],skip_models=[m1],include_models=[m2])
        t.judge([m1,m2])


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
        
        BooleanScore(True)
        BooleanScore(False)
        score = BooleanScore.compute(5,5)
        self.assertEqual(score.sort_key,1)
        score = BooleanScore.compute(4,5)
        self.assertEqual(score.sort_key,0)

        score = FloatScore(3.14)
        obs = np.array([1.0,2.0,3.0])
        pred = np.array([1.0,2.0,4.0])
        score = FloatScore.compute_ssd(obs,pred)
        self.assertEqual(score.score,1.0)
        
        RatioScore(1.2)
        score = RatioScore.compute({'mean':4,'std':1},{'value':2})
        self.assertEqual(score.score,0.5)

        score = PercentScore(42)
        self.assertTrue(score.sort_key,0.42)

        ZScore(0.7)
        score = ZScore.compute({'mean':3,'std':1},{'value':2})
        self.assertEqual(score.score,-1)

        CohenDScore(-0.3)
        score = CohenDScore.compute({'mean':3,'std':1},{'mean':2,'std':1})
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
    @unittest.skipIf(platform.python_version()<'3.9',
                     "run-nb not supported on Python < 3.3")
    def test_sciunit_5run_nb(self):
        self.main('--directory',self.cosmosuite_path,'run-nb')


class ExampleTestCase(unittest.TestCase):
    """Unit tests for example modules"""

    def test_example1(self):
        from sciunit.tests import example


if __name__ == '__main__':
    unittest.main()
