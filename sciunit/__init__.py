# TODO: Licensing header
# TODO: License files in repository root.
"""sciunit: A Framework for Formal Validation of Scientific Models"""

#
# Exceptions
#

class Error(Exception):
    """Base class for errors in sciunit."""

class NotImplementedError(Error, NotImplementedError): #@ReservedAssignment
    """Raised when calling an abstract method for which an implementation has
    not been supplied.
    
    Inherits from both :class:`Error` and the Python standard 
    :class:`NotImplementedError` exception classes.
    """
    
class AbstractBaseClassError(Error):
    """Raised when sciunit detects that a class inherits directly from an 
    abstract base class (that is, a class that exists only to serve as a 
    common base class for its more specific subclasses."""
    pass

#
# Tests 
#

class Test(object):
    """Abstract base class for tests."""
    def run_test(self, model):
        raise NotImplementedError("Must supply a run_test method.")
    
    @classmethod
    def validate_score(cls, score):
        raise AbstractBaseClassError("""Test is an abstract base class. 
            Tests should inherit from a specific subclass of Test.""")

class BooleanTest(Test):
    """Tests which return boolean scores should implement this interface."""
    def run_test(self, model):
        raise NotImplementedError("Must supply a run_test method.")

    @classmethod
    def validate_score(cls, score):
        return isinstance(score, bool)
    
class PercentageTest(Test):
    """Tests which return percentage scores, from 0.0 to 1.0 inclusive, with 
    1.0 being the best, should implement this interface."""
    def run_test(self, model):
        raise NotImplementedError("Must supply a run_test method.")

    @classmethod
    def validate_score(cls, output):
        return 0.0 <= output <= 1.0

class NormalizedMetricTest(Test):
    """Tests that return a normalized metric, from 0.0 to 1.0 inclusive, that 
    should NOT be interpretted as a percentage should implement this 
    interface."""
    def run_test(self, model):
        raise NotImplementedError("Must supply a run_test method.")

    @classmethod
    def validate_score(cls, output):
        return 0.0 <= output <= 1.0

#
# Capabilities
#

class Capability(object):
    """Abstract base class for sciunit capabilities."""
    @property
    def name(self):
        return self.__class__.__name__
    
class LacksCapabilityError(Error):
    def __init__(self, capability, *args):
        self.capability = capability
        Error.__init__(self, *args)
        
def require(model, capabilities):
    for capability in capabilities:
        if not isinstance(model, capability):
            raise LacksCapabilityError(capability, 
                "Model lacks capability: %s." % capability.name)

