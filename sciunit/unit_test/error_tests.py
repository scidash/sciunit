"""Unit tests for sciunit errors"""

import unittest


class ErrorsTestCase(unittest.TestCase):
    """Unit tests for various error classes"""

    def test_error_types(self):
        from sciunit.errors import (
            CapabilityError,
            BadParameterValueError,
            PredictionError,
            InvalidScoreError,
        )
        from sciunit import Model, Capability

        CapabilityError(Model(), Capability)
        CapabilityError(Model(), Capability, "this is a test detail")
        PredictionError(Model(), "foo")
        InvalidScoreError()
        BadParameterValueError("x", 3)


if __name__ == "__main__":
    unittest.main()
