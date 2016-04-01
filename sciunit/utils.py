"""
Utility functions for SciUnit.
"""

from __future__ import print_function
from quantities.dimensionality import Dimensionality
from quantities.quantity import Quantity

PRINT_DEBUG_STATE = False # printd does nothing by default.  

def printd_set(state):
    global PRINT_DEBUG_STATE
    PRINT_DEBUG_STATE = (state is True)

def printd(*args, **kwargs):
    global PRINT_DEBUG_STATE
    if PRINT_DEBUG_STATE:
        print(*args, **kwargs)

def assert_dimensionless(value):
    """
    Tests for dimensionlessness of input.
    If input is dimensionless but expressed as a Quantity, it returns the 
    bare value.  If it not, it raised an error.
    """
    if type(value) is Quantity:
        value = value.simplified
        if value.dimensionality == Dimensionality({}):
            value = value.base.item()
        else:
            raise TypeError("Score value %s must be dimensionless" % value)
    return value