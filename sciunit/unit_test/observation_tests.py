"""Unit tests for observations."""

import unittest

from sciunit.utils import NotebookTools


class ObservationsTestCase(unittest.TestCase, NotebookTools):
    """Unit tests for the sciunit module"""

    path = "."

    def test_observation_validation(self):
        """Test validation of observations against the `observation_schema`."""
        self.do_notebook("validate_observation")
