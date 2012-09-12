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
# Models
# 
class Model(object):
    """Abstract base class for sciunit models."""
    
#
# Capabilities
#
class Capability(object):
    """Abstract base class for sciunit capabilities."""
    @property
    def name(self):
        return self.__class__.__name__

    @classmethod
    def check(cls, model):
        """Checks whether the provided model has this capability.

        By default, uses isinstance.
        """
        return isinstance(model, cls)
    
def check_capabilities(test, model):
    assert isinstance(test, Test)
    assert isinstance(model, Model)

    for c in test.required_capabilities:
        c.check(model)

#
# Running Tests
#
def run(test, model):
    """Runs the given test on the given model.

    1. Runs check_capabilities(test, model)
    2. Produces a score by calling the run_test method.
    3. Returns a TestResult containing the score.
    """
    # Check capabilities
    check_capabilities(test, model)

    # Run test
    score = test.run_test(model)
    assert isinstance(score, Score)

    # Return a TestResult wrapping the score
    return TestResult(test, model, score)

class TestResult(object):
    """Represents the result of running a test on a model."""
    def __init__(self, test, model, score):
        assert isinstance(test, Test)
        assert isinstance(model, Model)
        assert isinstance(score, Score)
        self.test, self.model, self.score = test, model, score

    test = None
    """The test taken."""

    model = None
    """The model tested."""

    score = None 
    """The score produced."""
