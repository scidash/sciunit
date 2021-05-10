"""Unit tests for sciunit utility functions and classes"""

import tempfile
import unittest


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
