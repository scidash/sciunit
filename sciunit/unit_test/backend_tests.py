"""Unit tests for backends."""

from sciunit.utils import NotebookTools
import unittest


class BackendsTestCase(unittest.TestCase, NotebookTools):
    """Unit tests for the sciunit module"""

    path = '.'

    def test_backends(self):
        """Test backends."""
        self.do_notebook('backend_tests')