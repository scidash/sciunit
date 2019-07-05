"""Unit tests for sciunit utility functions and classes"""

import unittest
import tempfile


class UtilsTestCase(unittest.TestCase):
    """Unit tests for sciunit.utils"""

    def test_log(self):
        from sciunit.utils import log

        log("Lorem Ipsum")

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
        from sciunit.base import SciUnit

        d1 = {'a': 1, 'b': 2, 'c': 3}
        d2 = {'c': 3, 'a': 1, 'b': 2}
        dh1 = SciUnit.dict_hash(d1)
        dh2 = SciUnit.dict_hash(d2)
        self.assertTrue(type(dh1) is str)
        self.assertTrue(type(dh2) is str)
        self.assertEqual(d1, d2)

    def test_import_module_from_path(self):
        from sciunit.utils import import_module_from_path

        temp_file = tempfile.mkstemp(suffix='.py')[1]
        with open(temp_file, 'w') as f:
            f.write('value = 42')
        module = import_module_from_path(temp_file)
        self.assertEqual(module.value, 42)

    def test_versioned(self):
        from sciunit.models.examples import ConstModel

        m = ConstModel(37)
        print("Commit hash is %s" % m.version)
        print("Remote URL is %s" % m.remote_url)
        self.assertTrue('sciunit' in m.remote_url)
