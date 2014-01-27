"""sciunit: A Framework for Formal Validation of Scientific Models"""

from collections import Callable

#
# Tests 
#

class Test(object):
	"""Abstract base class for tests."""
	def __init__(self, name=None):
			if name is None:
				name = self.__class__.__name__
			self.name = Name

			if self.description is None:
				self.description = self.__class__.__doc__

	name = None
	"""The name of the test. Defaults to the test class name."""

	description = None
	"""A description of the test. Defaults to the docstring for the test class."""
  
	required_capabilities = ()
	"""A sequence of capabilities that a model must have in order for the 
	test to be run. Defaults to empty."""

	def _judge(self, model):
		"""The main testing function.

		Takes a Model as input and produces a Score as output. 
		No default implementation. Must be provided by test implementor.
		"""
		raise NotImplementedError("Must supply a _judge method.")

	def judge(self, model, fail_silently=False):
		"""Makes the provided model take the provided test.

		Operates as follows:
		1. Invokes check_capabilities(test, model). 
		     If fail_silently is True, the method returns None when this fails.
		     Otherwise, raises a CapabilityError.
		2. Produces a score by calling the _judge method. Checks that the method
		   actually returns a Score, raising an InvalidScoreError if not.

		Do not override; override _judge only.
		"""
		# Check capabilities
		try:
			check_capabilities(self, model)
		except CapabilityError,e:
			if fail_silently:
				return None
			else:
				raise e

		# Run test
		print "Running test."
		score = self._judge(model)
		check_score(score)
		if score.test is None:
			score.test = self
		if score.model is None:
			score.model = model
		return score

#
# Test Suites
#

class TestSuite(object):
	"""A collection of tests."""

	def __init__(self, tests, name=None):
		# turn singleton test into a sequence
		if isinstance(tests, Test):
			tests = (tests,)
		else:
			for test in tests:
				assert isinstance(test, Test)
		self.tests = tests

		if name is None:
			name = self.__class__.__name__
		self.name = name

  name = None
  """The name of the test suite. Defaults to the class name."""

  description = None
  """The description of the test suite. No default."""

	tests = None
	"""The sequence of tests that this suite contains."""

	def judge(self,models,summarize=True):
		"""Judges the provided models against each test in the test suite.

		Returns a ScoreMatrix.
		"""
		if isinstance(models, Model):
			models = (models,)
		matrix = ScoreMatrix(self.tests, models)
		for test in self.tests:
			for model in models:
				matrix[test, model] = test.judge(model)
		return matrix

#
# Scores
#

class Score(object):
	"""Abstract base class for scores.

	Pairs a score value with the test and model that produced it."""
	
	def __init__(self, score, related_data={}):
		self.score, self.related_data = score, related_data
	
	score = None
	"""The score itself."""

	related_data = {}
	"""Data specific to the result of a test run on a model."""

	test = None
	"""The test taken. Set automatically by Test.judge."""

	model = None
	"""The model judged. Set automatically by Test.judge."""

	@property
	def summary(self):
		"""Summarize the performance of a model on a test."""
		return "Model '%s' achieved score %s on test '%s'." % (self.model.name,
														  self.__str__(),
														  self.test.name)

	def summarize(self):
		print self.summary

	def __str__(self):
		return u'%s' % self.score

class InvalidScoreError(Exception):
	"""Error raised when a score is invalid."""

def check_score(score):
	if not isinstance(score, Score):
		raise InvalidScoreError()

#
# Models
#

class Model(object):
	"""Abstract base class for sciunit models."""
	def __init__(self, name=None):
		if name is None:
			name = self.__class__.__name__
		self.name = name

	name = None
	"""The name of the model. Defaults to the class name."""
	
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
	to statistical summaries of model data.  They issue a score indicating the
	result of that comparison, e.g. a Z-score."""
	def __init__(self, converter=None): 
		"""A comparator is instantiated with the test and model whose 
		reference data (the test) and output (the model) will be compared."""

		if converter is not None and not isinstance(converter, Callable):
			raise InvalidComparatorError("converter must be a function or \
										  instance method.")
		else:
			self.converter = converter
			"""Conversion to apply to primary score type.  
			See sciunit.Comparators.""" 

		if Score not in self.score_type.mro():
			raise InvalidComparatorError("Score attribute must be a descendant \
										 of sciunit.Score.") 
			 
	score_type = Score
	"""Primary score type for a comparator of this class, before any conversion.  
	See sciunit.Scores."""  
		
	required_output_stats = ()
	"""Statistics the test must extract from the model output for comparison 
	to the reference data to use a comparator of this class."""
	
	required_reference_stats = ()
	"""Statistics the test must extract from the reference data for comparison 
	to the model output to use a comparator of this class."""
		
	def compare(self,
				test,
				model,
				**kwargs):
		"""Compare test reference stats and model output stats
		to produce a score."""

		if not hasattr(model,'output_stats'):
			raise InvalidComparatorError("model must have derived \
										  attribute output_stats.")
		
		if not hasattr(test,'reference_stats'):
			raise InvalidComparatorError("test must have derived \
										  attribute output_stats.")
			
		if type(model.output_stats) is not dict:
			"""Dictionary of statistics from e.g. model run(s)."""
			raise InvalidComparatorError("output_stats must be a dict.")
			
		if type(test.reference_stats) is not dict:
			"""Dictionary of statistics from the reference model/data."""
			raise InvalidComparatorError("reference_stats must be a dict.")
		
		for key in self.required_output_stats:
			if key not in model.output_stats.keys():
				raise InvalidComparatorError("'%s' not found in the \
											 model.output_stats dict." % key)
		
		for key in self.required_reference_stats:
			if key not in test.reference_stats.keys():
				raise InvalidComparatorError("'%s' not found in the \
											 test.reference_stats dict." % key) 

		raw = self.compute(test.reference_stats,model.output_stats,**kwargs)
		return self.score(raw,test,model,**kwargs)
		
	def compute(self,
				reference_stats,
				output_stats,
				**kwargs):
		"""Computes a raw comparison statistic (e.g. a Z-score) from 
		the model's output_stats and the test's reference_stats."""  
		
		raise NotImplementedError("No Comparator computing function has \
								   been implemented.")

	def score(self,
			  raw,
			  test,
			  model,
			  **params):
		"""A converter can convert one (raw) score into another 
		Score subclass.  
		params are used by this converter to map scores appropriately."""
		if self.converter:
			value = self.converter(raw,**params)
		else:
			value = raw
		related_data = params['related_data'] \
					   if 'related_data' in params.keys() else {}
		score = self.score_type(value,test,model,related_data=related_data)
		return score
		
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
	"""Error raised when a required capability is not 
	provided by a model."""
	def __init__(self, model, capability):
		self.model = model
		self.capability = capability

		super(CapabilityError,self).__init__(\
			"Model %s does not provide required capability: %s" % \
			(model.name,capability().name))
	
	model = None
	"""The model that does not have the capability."""

	capability = None
	"""The capability that is not provided."""

def check_capabilities(test, model):
	"""Checks that the capabilities required by `test` are 
	implemented by `model`.

	First checks that `test` is a `Test` and `model` is a `Model`.
	"""
	assert isinstance(test, Test)
	assert isinstance(model, Model)

	for c in test.required_capabilities:
		if not c.check(model):
			raise CapabilityError(model, c)

	print "Model possesses required capabilities."
	return True

