"""Unit tests for SciUnit"""

# Run with any of:  
# python test_all.py
# python -m unittest test_all.py

# coverage run --source . test_all.py

import unittest

from sciunit.utils import NotebookTools


class DocumentationTestCase(NotebookTools,unittest.TestCase):

    path = 'docs'

    def test_chapter1(self):
        self.do_notebook('chapter1')
    
    def test_chapter2(self):
        self.do_notebook('chapter2')
    
    def test_chapter3(self):
        self.do_notebook('chapter3')


class ImportTestCase(unittest.TestCase):
    def test_quantities(self):
        import quantities


if __name__ == '__main__':
    unittest.main()
