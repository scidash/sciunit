from scipy.stats import norm

"""sciunit: A Framework for Formal Validation of Scientific Models"""

#
# Tests 
#

class Test(object):
    """Abstract base class for tests."""

    comparator = None
    """Comparator from sciunit.Comparators."""

    converter = None
    """Optional Converter from sciunit.Comparators."""

    conversion_params = {}
    """Optional conversion parameters for the Converter."""
    
    reference_data = {}
    """A dictionary of data that the tests references to compare model output against."""

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
    """A collection of tests."""

    def __init__(self, tests):
        for test in tests:
            assert isinstance(test, Test)
        self.tests = tests
        
    tests = None
    """The sequence of tests that this suite contains."""
    
# 
# Score Maps  
# These are responsible for converting statistical summaries of tests, e.g. mean and sd, into scores, e.g. pass/fail or 0-100.  
#

class InvalidComparatorError(Exception):
    """Error raised when the comparator provided in the constructor is invalid."""

class Comparator():
    """Abstract base class for comparators."""
    def __init__(self,model_stats,reference_stats):
        if (type(model_stats),type(reference_stats)) is not (dict,dict):
            raise InvalidComparatorError("model_stats and reference_stats must both be dictionaries.")
        for key in required_model_stats:
            if key not in model_stats.keys():
                raise InvalidComparatorError("'%s' not found in the model_stats dictionary" % key)
        for key in required_model_stats:
            if key not in reference_stats.keys():
                raise InvalidComparatorError("'%s' not found in the reference_stats dictionary" % key)
        for key,value in locals().items():
            self.__setattr__(key,value)

    score_type = None # Primary score type for a comparator, before any conversion.  See sciunit.Scores.  
    converter = None # Conversion to apply to primary score type.  See sciunit.Comparators.  
    required_model_stats = ()
    required_reference_stats = ()
    model_stats = None # Dictionary of statistics from e.g. model run(s).  
    reference_stats = None # Dictionary of statistics from the reference model/data.  

    def compute(self,**kwargs):
        """Computes a raw comparison statistic (e.g. a Z-score) from model_stats and reference_stats."""  
        raise NotImplementedError("No Comparator computing function has been implemented.")

    def score(self,**params):
        """A converter can convert one (raw) score into another Score subclass.  
        params are used by this converter to map scores appropriately."""
        raw = self.compute()
        score = self.score_type(raw)
        if self.converter:
            score = self.converter(score,params)
        return score
        
#
# Scores
#

class InvalidScoreError(Exception):
    """Error raised when the score provided in the constructor is invalid."""

class Score(object):
    """Abstract base class for scores."""
    def __init__(self, score):
        self.score = score

    score = None
    """The score itself."""

    reference_data = None
    """A dictionary of related data."""

    model_data = None
    """A dictionary of model data."""

#
# Models
#

class Model(object):
    """Abstract base class for sciunit models."""
    name = None # String containing name of the model.  

    def __str__(self):
        return u'%s' % self.name # Return names as unicode-encoded strings, always.  
#
# Capabilities
#

class Capability(object):
    """Abstract base class for sciunit capabilities."""
    @property
    def name(self):
        """The name of the capability.

        Defaults to the class name."""
        return self.__class__.__name__

    @classmethod
    def check(cls, model):
        """Checks whether the provided model has this capability.

        By default, uses isinstance.
        """
        return isinstance(model, cls)

class CapabilityError(Exception):
    """Error raised when a required capability is not provided by a model."""
    def __init__(self, model, capability):
        self.model = model
        self.capability = capability

        Exception.__init__("Model does not provided required capability: %s"
            % capability.name)
    
    model = None
    """The model that does not have the capability."""

    capability = None
    """The capability that is not provided."""

def check_capabilities(test, model):
    """Checks that the capabilities required by `test` are implemented by `model`.

    First checks that `test` is a `Test` and `model` is a `Model`.
    """
    assert isinstance(test, Test)
    assert isinstance(model, Model)

    for c in test.required_capabilities:
        if not c.check(model):
            raise CapabilityError(model, c)

    return True

#
# Running Tests
#

def run(test, model):
    """Runs the provided test on the provided model.

    Operates as follows:
    1. Invokes check_capabilities(test, model).
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
    """Pairs a score with the test and model that produced it."""
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
