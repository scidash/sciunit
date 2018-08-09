"""Unit tests for observations."""

from sciunit.utils import NotebookTools
import unittest


class ObservationsTestCase(unittest.TestCase, NotebookTools):
    """Unit tests for the sciunit module"""

    path = '.'

    def test_observation_validation(self):
        """Test validation of observations against the `observation_schema`."""
        self.do_notebook('validate_observation')
