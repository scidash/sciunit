"""Unit tests for sciunit utility functions and classes"""

import tempfile
import unittest

import sciunit
from sciunit.utils import use_backend_cache
import numpy as np


class CacheTestCase(unittest.TestCase):

    def test_basic_cache(self):
        class dummy_test(sciunit.Test):

            # The name of the cache key param determines the cache key location
            @use_backend_cache(cache_key_param='dummy_cache_key')
            def create_random_matrix(self, model):
                # Generate a random matrix that will land in cache
                return np.random.randint(0, 100, size=(5,5))

        class dummy_avg_test(dummy_test):

            default_params = {'dummy_cache_key': '1234'}

            @use_backend_cache
            def generate_prediction(self, model):
                return np.mean(self.create_random_matrix(model))

        class dummy_std_test(dummy_test):

            default_params = {'dummy_cache_key': '1234'}

            @use_backend_cache
            def generate_prediction(self, model):
                return np.std(self.create_random_matrix(model))

            @use_backend_cache
            def warning_function(self):
                return 'I am supposed to fail, because I have no model'

        class dummy_backend(sciunit.models.backends.Backend):
            pass

        class dummy_model(sciunit.models.RunnableModel):
            pass


        # Initialize dummy tests and models
        avg_corr_test1 = dummy_avg_test([], dummy_cache_key='1234')
        avg_corr_test2 = dummy_avg_test([], dummy_cache_key='5678')
        std_corr_test = dummy_std_test([])
        modelA = dummy_model(name='modelA', backend=dummy_backend)
        modelB = dummy_model(name='modelB', backend=dummy_backend)

        # Run predictions for the first time
        avg_corrsA1 = avg_corr_test1.generate_prediction(model=modelA)
        avg_corrsA2 = avg_corr_test2.generate_prediction(modelA)
        cached_predictionA1_avg = avg_corr_test1.get_backend_cache(model=modelA)
        cached_predictionA2_avg = avg_corr_test2.get_backend_cache(model=modelA)
        dummy_matrixA1 = avg_corr_test1.get_backend_cache(model=modelA,
                                                          key='1234')
        dummy_matrixA2 = avg_corr_test2.get_backend_cache(model=modelA,
                                                          key='5678')
        # dummy matrix is already generated
        # and cached specific for modelA with key '1234'
        std_corrsA = std_corr_test.generate_prediction(modelA)
        cached_predictionA_std = std_corr_test.get_backend_cache(model=modelA)
        dummy_matrixA_std = std_corr_test.get_backend_cache(model=modelA,
                                                         key='1234')

        # Check if cached predictions are equal to original computations
        self.assertTrue(avg_corrsA1 == cached_predictionA1_avg)
        self.assertTrue(std_corrsA == cached_predictionA_std)

        # Check that different tests yield different predictions
        # These are floats, unlikely to ever be the same by chance
        self.assertTrue(cached_predictionA1_avg != cached_predictionA2_avg)
        self.assertTrue(cached_predictionA1_avg != cached_predictionA_std)

        # Check cached matrices are the same
        self.assertTrue(np.any(dummy_matrixA1 != dummy_matrixA2))
        self.assertTrue(np.all(dummy_matrixA1 == dummy_matrixA_std))

        """Check that a different model will have a different chache"""
        avg_corrsB = avg_corr_test1.generate_prediction(modelB)
        cached_predictionB1_avg = avg_corr_test1.get_backend_cache(model=modelB)
        dummy_matrixB1 = avg_corr_test1.get_backend_cache(model=modelB,
                                                         key='1234')
        self.assertTrue(cached_predictionA1_avg != cached_predictionB1_avg)
        self.assertTrue(np.any(dummy_matrixA1 != dummy_matrixB1))

        """Test the failing cases of the decorator"""
        with self.assertWarns(Warning):
            std_corr_test.warning_function()

        with self.assertWarns(Warning):
            test = dummy_test([])
            test.create_random_matrix(modelA)

class UtilsTestCase(unittest.TestCase):
    """Unit tests for sciunit.utils"""

    def test_warnings_traceback(self):
        from sciunit.utils import set_warnings_traceback, warn_with_traceback

        set_warnings_traceback(True)
        warn_with_traceback("This is a test warning", Warning, "utils_tests.py", 13)

        set_warnings_traceback(False)
        warn_with_traceback("This is a test warning", Warning, "utils_tests.py", 16)

    def test_notebook(self):
        from sciunit.utils import NotebookTools

        notebookObj = NotebookTools()
        notebookObj.execute_notebook("../docs/chapter1")

    def test_log(self):
        from sciunit.base import log, strip_html
        from sciunit.utils import html_log

        str1 = "<b>test log 1</b>"
        str1_stripped = "test log 1"
        str2 = "<i>test log 2</i>"
        self.assertEqual(strip_html(str1), str1_stripped)
        log(str1_stripped)
        html_log(str1, str2)

    def test_assert_dimensionless(self):
        import quantities as pq

        from sciunit.utils import assert_dimensionless

        assert_dimensionless(3 * pq.s * pq.Hz)
        try:
            assert_dimensionless(3 * pq.s)
        except TypeError:
            pass
        else:
            raise Exception("Should have produced a type error")

    def test_dict_hash(self):
        from sciunit.utils import dict_hash

        d1 = {"a": 1, "b": 2, "c": 3}
        d2 = {"c": 3, "a": 1, "b": 2}
        dh1 = dict_hash(d1)
        dh2 = dict_hash(d2)
        self.assertTrue(type(dh1) is str)
        self.assertTrue(type(dh2) is str)
        self.assertEqual(d1, d2)

    def test_import_module_from_path(self):
        from sciunit.utils import import_module_from_path

        temp_file = tempfile.mkstemp(suffix=".py")[1]
        with open(temp_file, "w") as f:
            f.write("value = 42")
        module = import_module_from_path(temp_file)
        self.assertEqual(module.value, 42)

    def test_versioned(self):
        from sciunit.models.examples import ConstModel

        m = ConstModel(37)
        print("Commit hash is %s" % m.version)
        print("Remote URL is %s" % m.remote_url)
        self.assertTrue("sciunit" in m.remote_url)

    def test_MockDevice(self):
        from io import StringIO

        from sciunit.utils import MockDevice

        s = StringIO()
        myMD = MockDevice(s)
        myMD.write("test mock device writing")

    def test_memoize(self):
        from random import randint

        from sciunit.utils import memoize

        @memoize
        def f(a):
            return a + randint(0, 1000000)

        # Should be equal despite the random integer
        # because of memoization
        self.assertEqual(f(3), f(3))

    def test_intern(self):
        from sciunit.utils import class_intern

        class N:
            def __init__(self, n):
                self.n = n

        five = N(5)
        five2 = N(5)
        self.assertNotEqual(five, five2)

        # Add the decorator to the class N.
        N = class_intern(N)

        five = N(5)
        five2 = N(5)
        self.assertEqual(five, five2)


if __name__ == "__main__":
    unittest.main()
