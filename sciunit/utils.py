"""
Utility functions for SciUnit.
"""

from quantities.dimensionality import Dimensionality
from quantities.quantity import Quantity

def assert_dimensionless(value):
    """
    Tests for dimensionlessness of input.
    If input is dimensionless but expressed as a Quantity, it returns the 
    bare value.  If it not, it raised an error.
    """
    if type(value) is Quantity:
        if value.dimensionality == Dimensionality({}):
            value = value.base.item()
        else:
            raise TypeError("Score value %s must be dimensionless" % value)
    return value