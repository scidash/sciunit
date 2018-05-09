"""Unit tests for sciunit errors"""

import unittest

class ErrorsTestCase(unittest.TestCase):
    """Unit tests for various error classes"""
    
    def test_error_types(self):
        from sciunit.errors import CapabilityError, BadParameterValueError,\
                                   PredictionError, InvalidScoreError
        from sciunit import Model, Capability

        CapabilityError(Model(),Capability)
        PredictionError(Model(),'foo')
        InvalidScoreError()
        BadParameterValueError('x',3)
        
