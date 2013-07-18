from __future__ import unicode_literals

"""sciunit: A Framework for Formal Validation of Scientific candidates"""

from collections import Callable

#
# Tests 
#

class Test(object):
	"""Abstract base class for tests."""
	
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

		Takes a Candidate as input and produces a Score as output. 
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

	related_data = {}
	"""Data specific to the result of a test run on a candidate."""
	
# 
# Comparators
# These are responsible for converting statistical summaries of tests, 
# e.g. mean and sd, into scores, e.g. PASS/FAIL or 0-100.  
#

class InvalidComparatorError(Exception):
	"""Error raised when the comparator provided in the constructor is invalid."""

class Comparator(object):
	"""Abstract base class for comparators.
	Comparators are used to compare statistical summaries of reference data
	to statistical summaries of candidate data.  They issue a score indicating the
	result of that comparison, e.g. a Z-score."""
	def __init__(self,converter=None): 
		if converter is not None and not isinstance(converter, Callable):
			raise InvalidComparatorError("converter must be a function or \
										  instance method.")
		else:
			self.converter = converter
			"""Conversion to apply to primary score type.  
			See sciunit.Comparators.""" 

		for key in self.required_candidate_stats:
			if key not in candidate_stats.keys():
				raise InvalidComparatorError("'%s' not found in the \
											 candidate_stats dictionary" % key)
		for key in self.required_reference_stats:
			if key not in reference_stats.keys():
				raise InvalidComparatorError("'%s' not found in the \
											 reference_stats dictionary" % key) 

		if Score not in self.score_type.mro():
			raise InvalidComparatorError("Score attribute must be a descendant \
										 of sciunit.Score.") 
			 
	score_type = Score
	"""Primary score type for a comparator of this class, before any conversion.  
	See sciunit.Scores."""  
		
	required_candidate_stats = ()
	"""Statistics the test must extract from the candidate output for comparison 
	to the reference data to use a comparator of this class."""
	
	required_reference_stats = ()
	"""Statistics the test must extract from the reference data for comparison 
	to the candidate output to use a comparator of this class."""
		
	def compare(self,candidate_stats,reference_stats,**kwargs):
		if type(candidate_stats) is not dict:
			raise InvalidComparatorError("candidate_stats must be a dictionary.")
		else:
			self.candidate_stats = candidate_stats
			"""Dictionary of statistics from e.g. candidate run(s)."""
	
		if type(reference_stats) is not dict:
			raise InvalidComparatorError("reference_stats must be a dictionary.")
		else:
			self.reference_stats = reference_stats
			"""Dictionary of statistics from the reference candidate/data."""
		try:
			raw = self.compute(**kwargs)
			return self.score(raw,**kwargs)
		except Exception,e:
			raise e

	def compute(self,**kwargs):
		"""Computes a raw comparison statistic (e.g. a Z-score) from 
		candidate_stats and reference_stats."""  
		raise NotImplementedError("No Comparator computing function has \
								   been implemented.")

	def score(self,raw,**params):
		"""A converter can convert one (raw) score into another 
		Score subclass.  
		params are used by this converter to map scores appropriately."""
		score = self.score_type(raw)
		if self.converter:
			score = self.converter(score,**params)
		return score
		
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
	"""Error raised when a required capability is not 
	provided by a candidate."""
	def __init__(self, candidate, capability):
		self.candidate = candidate
		self.capability = capability

		print capability
		print capability.name
		super(CapabilityError,self).__init__(\
			"Candidate %s does not provide required capability: %s" % \
			(candidate.name,capability().name))
	
	candidate = None
	"""The candidate that does not have the capability."""

	capability = None
	"""The capability that is not provided."""

def check_capabilities(test, candidate):
	"""Checks that the capabilities required by `test` are 
	implemented by `candidate`.

	First checks that `test` is a `Test` and `candidate` is a `Candidate`.
	"""
	print "Checking candidate capabilities."
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
	print "Running test."
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
		print "Candidate '%s' achieved score %s on test '%s'." % (self.candidate.name,
														  self.score,
														  self.test.name)
