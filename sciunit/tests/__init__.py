"""SciUnit tests live in this module."""
import sciunit
import sciunit.capabilities

class ComparatorTest(sciunit.Test):
	"""A standard test class that encourages the use of Comparators."""
	def __init__(self,comparator):
		self.comparator = comparator()
		"""Comparator from sciunit.Comparators."""

class PositivityTest(sciunit.Test):
	"""Checks whether the candidate produces a positive value."""

	required_capabilities = (sciunit.capabilities.ProducesNumber,)

	def run_test(self, candidate):
		"""The main testing function."""
		data = candidate.produce_data()
		return BooleanScore(data > 0, {"data": data})

class StandardTest(ComparatorTest):
	"""The first test class that will be useful."""
	def __init__(self,reference_data,candidate_args,comparator):
		"""reference_data are summary statistics of reference data.
		candidate_args are arguments used by the candidate to run 
		or fit itself."""
		super(StandardTest,self).__init__(comparator)
		self.reference_data.update(reference_data) # Store reference data. 
		self.candidate_args.update(candidate_args) # Store candidate arguments.  
		self.required_capabilities += (sciunit.capabilities.Runnable,)
		
	def pre_checks(self):
		"""Checks that the test has everything it needs to run properly."""
		assert sciunit.Comparator in self.comparator.__class__.mro()

	def run_test(self,candidate,**kwargs):
		"""Runs the test and returns a score."""
		self.pre_checks()
		candidate.run(**kwargs) # Run implementation guaranteed by Runnable capability.  
		candidate_data = self.get_candidate_data(candidate)
		return self.generate_score(candidate_data)
		
	def get_candidate_data(self,candidate):
		"""Extracts raw data from the candidate using Capabilities and returns it."""
		candidate_data = {}
		# Get candidate_data from the candidate...
		return candidate_data

	def get_candidate_stats(self,candidate_data):
		"""Puts candidate stats in a form that the Comparator will understand."""
		return {key:value for key,value in self.candidate_data} # This example is trivial.  
		
	def get_reference_stats(self):
		"""Puts reference stats in a form that the Comparator will understand."""
		return {key:value for key,value in self.reference_data} # This example is trivial.  
		
	def generate_score(self,candidate_data):
		"""Generate a score using some Comparator applied to the data."""
		candidate_stats = self.get_candidate_stats(candidate_data)
		reference_stats = self.get_reference_stats()
		score = self.comparator.compare(candidate_stats,reference_stats)
		score.candidate_data = candidate_data
		score.reference_data = self.reference_data
		return score
	