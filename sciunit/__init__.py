import types

"""sciunit: A Framework for Formal Validation of Scientific candidates"""

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
    """A dictionary of data that the tests references to compare candidate output against."""

    candidate_args = {}
    """A dictionary of arguments the candidate might use at run-time."""

    required_capabilities = ()
    """A sequence of capabilities that a candidate must have in order for the 
    test to be run. Defaults to empty."""

    @property
    def name(self):
        """The name of the test.

        Defaults to the class name."""
        return self.__class__.__name__
   
    def run_test(self, candidate):
        """The main testing function.

        Takes a candidate as input and produces a score as output. 
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
# Comparators
# These are responsible for converting statistical summaries of tests, 
# e.g. mean and sd, into scores, e.g. PASS/FAIL or 0-100.  
#

class InvalidComparatorError(Exception):
    """Error raised when the comparator provided in the constructor is invalid."""

class Comparator(object):
    """Abstract base class for comparators."""
    def __init__(self,candidate_stats,reference_stats,converter=None):
        if type(candidate_stats) is not dict:
            raise InvalidComparatorError("candidate_stats must be a dictionary.")
        if type(reference_stats) is not dict:
            raise InvalidComparatorError("reference_stats must be a dictionary.")
        if converter is not None and not hasattr(converter,'__call__'):
            raise InvalidComparatorError("converter must be a function or \
                                         instance method.")
        for key in self.required_candidate_stats:
            if key not in candidate_stats.keys():
                raise InvalidComparatorError("'%s' not found in the \
                                             candidate_stats dictionary" % key)
        for key in self.required_reference_stats:
            if key not in reference_stats.keys():
                raise InvalidComparatorError("'%s' not found in the \
                                             reference_stats dictionary" % key)
        for key,value in locals().items():
            self.__setattr__(key,value)

    score_type = None
    """Primary score type for a comparator, before any conversion.  
    See sciunit.Scores."""  
    
    converter = None
    """Conversion to apply to primary score type.  
    See sciunit.Comparators."""  
    
    required_candidate_stats = ()
    """Statistics the test must extract from the candidate outputfor comparison 
    to the reference data."""
    
    required_reference_stats = ()
    """Statistics the test must extract from the reference data for comparison 
    to the candidate output."""

    candidate_stats = None
    """Dictionary of statistics from e.g. candidate run(s)."""
    
    reference_stats = None
    """Dictionary of statistics from the reference candidate/data.""" 

    def compute(self,**kwargs):
        """Computes a raw comparison statistic (e.g. a Z-score) from 
        candidate_stats and reference_stats."""  
        raise NotImplementedError("No Comparator computing function has \
                                   been implemented.")

    def score(self,**params):
        """A converter can convert one (raw) score into another 
        Score subclass.  
        params are used by this converter to map scores appropriately."""
        raw = self.compute()
        score = self.score_type(raw)
        if self.converter:
            score = self.converter(score,**params)
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
    """A dictionary of related reference data."""

    candidate_data = None
    """A dictionary of related candidate data."""

#
# candidates
#

class Candidate(object):
    """Abstract base class for sciunit candidates."""
    @property
    def name(self):
        """The name of the candidate.

        Defaults to the class name."""
        return self.__class__.__name__

    def __str__(self):
        return u'%s' % self.name # Return names as unicode-encoded 
                                 # strings, always.  
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
    def check(cls, candidate):
        """Checks whether the provided candidate has this capability.

        By default, uses isinstance.
        """
        return isinstance(candidate, cls)

class CapabilityError(Exception):
    """Error raised when a required capability is not provided by a candidate."""
    def __init__(self, candidate, capability):
        self.candidate = candidate
        self.capability = capability

        Exception.__init__("candidate does not provided required capability: %s"
            % capability.name)
    
    candidate = None
    """The candidate that does not have the capability."""

    capability = None
    """The capability that is not provided."""

def check_capabilities(test, candidate):
    """Checks that the capabilities required by `test` are 
    implemented by `candidate`.

    First checks that `test` is a `Test` and `candidate` is a `candidate`.
    """
    assert isinstance(test, Test)
    assert isinstance(candidate, Candidate)

    for c in test.required_capabilities:
        if not c.check(candidate):
            raise CapabilityError(candidate, c)

    return True

#
# Running Tests
#

def judge(test, candidate): # I want to reserve 'run' for the concept of runnability in a candidate.  
    """Makes the provided candidate take the provided test.

    Operates as follows:
    1. Invokes check_capabilities(test, candidate).
    2. Produces a score by calling the run_test method.
    3. Returns a TestResult containing the score.
    """
    # Check capabilities
    check_capabilities(test, candidate)

    # Run test
    score = test.run_test(candidate)
    assert isinstance(score, Score)

    # Return a TestResult wrapping the score
    return TestResult(test, candidate, score)

class TestResult(object):
    """Pairs a score with the test and candidate that produced it."""
    def __init__(self, test, candidate, score):
        assert isinstance(test, Test)
        assert isinstance(candidate, Candidate)
        assert isinstance(score, Score)
        self.test, self.candidate, self.score = test, candidate, score

    test = None
    """The test taken."""

    candidate = None
    """The candidate tested."""

    score = None 
    """The score produced."""

    def summarize(self):
        """Summarize the performance of a candidate on a test."""
        print "candidate %s achieved score %s on test %s." % (self.candidate.name,
                                                          self.score,
                                                          self.test.name)
