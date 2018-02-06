"""Unit tests for documentation"""

import unittest
from sciunit.utils import NotebookTools

class DocumentationTestCase(NotebookTools,unittest.TestCase):
    """Unit tests for documentation notebooks"""

    path = '../../docs'

    def test_chapter1(self):
        self.do_notebook('chapter1')
    
    def test_chapter2(self):
        self.do_notebook('chapter2')
    
    def test_chapter3(self):
        self.do_notebook('chapter3')