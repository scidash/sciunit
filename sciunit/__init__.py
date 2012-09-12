# TODO: Licensing header
# TODO: License files in repository root.
"""sciunit: A Framework for Formal Validation of Scientific Models"""

#
# Tests 
#

class Test(object):
    """Abstract base class for tests."""
    required_capabilities = ()
    """A sequence of capabilities that a model must have in order for the 
    test to be run. Defaults to empty."""

    def run_test(self, model):
        """The main testing function.

        Takes a model as input and produces a score as output. 
        No default implementation.
        """
        raise NotImplementedError("Must supply a run_test method.")
    
#
# Test Suites
#
class TestSuite(object):
    def __init__(self, tests):
        for test in tests:
            assert isinstance(test, Test)
        self.tests = tests
        
    tests = None
    """The sequence of tests that this suite contains."""
    
#
# Scores
#
class InvalidScoreError(Exception):
    """Error raised when the score is invalid."""

class Score(object):
    """Abstract base class for scores."""
    def __init__(self, score, related_data):
        self.score = score
        self.related_data = related_data

    score = None
    """The score itself."""

    related_data = None
    """A dictionary of related data."""

class BooleanScore(Score):
    """A score with boolean value."""
    def __init__(self, score, related_data):
        if not isinstance(score, bool):
            raise InvalidScoreError("Score is not a boolean.")
        Score.__init__(self, score, related_data)
    
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

#
# Models
# 
class Model(object):
    """Abstract base class for sciunit models."""
    
#
# Running Tests
#
def run(self, t, m):
    # TODO: implement this
    pass

class TestResults(object):
    # TODO: implement this
    pass
