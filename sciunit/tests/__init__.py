"""SciUnit tests live in this module."""
from sciunit import Test
from sciunit.capabilities import Runnable

class RickTest(Test,Runnable):
	"""The kind of test that Rick is going to use."""
	def __init__(self,reference_data,candidate_args):
		"""reference_data are summary statistics of reference data.
		candidate_args are arguments used by the candidate to run 
		or fit itself."""
		self.reference_data.update(reference_data) # Store reference data. 
		self.candidate_args.update(candidate_args) # Store candidate arguments.  
		self.required_capabilities += (Runnable,)
	
	def pre_checks(self):
		"""Checks that the test has everything it needs to run properly."""
		assert self.comparator is not None

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
		comparator = self.comparator(candidate_stats,reference_stats,converter=self.converter) # A Z-score.
		score = comparator.score()
		score.candidate_data = candidate_data
		score.reference_data = self.reference_data
		return score
	