"""Unit tests for SciUnit"""

# Run with any of:  
# python test_all.py
# python -m unittest test_all.py

# coverage run --source . test_all.py

import unittest

from sciunit.utils import NotebookTools, import_all_modules


class DocumentationTestCase(NotebookTools,unittest.TestCase):

    path = '../docs'

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


if __name__ == '__main__':
    unittest.main()
