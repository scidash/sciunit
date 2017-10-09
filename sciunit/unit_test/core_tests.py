"""Unit tests for SciUnit"""

# Run with any of:  
# python test_all.py
# python -m unittest test_all.py

# coverage run --source . test_all.py

import unittest

from sciunit.utils import NotebookTools, import_all_modules


class DocumentationTestCase(NotebookTools,unittest.TestCase):

    path = '../../docs'

    def test_chapter1(self):
        self.do_notebook('chapter1')
    
    def test_chapter2(self):
        self.do_notebook('chapter2')
    
    def test_chapter3(self):
        self.do_notebook('chapter3')


class ImportTestCase(unittest.TestCase):
    def test_quantities(self):
        import quantities

    def test_import_everything(self):
        import sciunit
        # Recursively import all submodules
        import_all_modules(sciunit)


class UtilsTestCase(unittest.TestCase):
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


class CommandLineTestCase(unittest.TestCase):
    def setUp(self):
        from sciunit.__main__ import main
        self.main = main

    def test_scidash_create(self):
        try:
            self.main('--directory','/Users/rgerkin/dev/scidash/scidash','create')
        except OSError as e:
            if 'There is already a configuration file' not in str(e):
                raise e

    def test_scidash_run(self):
        self.main('--directory','/Users/rgerkin/dev/scidash/scidash','run')

    def test_scidash_make_nb(self):
        self.main('--directory','/Users/rgerkin/dev/scidash/scidash','make-nb')

    def test_scidash_run_nb(self):
        self.main('--directory','/Users/rgerkin/dev/scidash/scidash','run-nb')


class ExampleTestCase(unittest.TestCase):
    def test_example1(self):
        from sciunit.tests import example

if __name__ == '__main__':
    unittest.main()
