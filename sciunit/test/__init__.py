"""SciUnit tests live in this module."""
from sciunit import Test
from sciunit.comparators import ZComparator,IdentityScore,InvalidComparatorError

class RickTest(Test)
"""The kind of test that Rick is going to use."""
	required_capabilities += (capabilities.Runnable)
	def __init__(self,*args):
		"""Arguments are summary statistics of reference data."""
		for key,value in locals():
			self.reference_data[key] = value # Store constructor arguments as reference data.  

	def pre_checks(self):
		assert self.comparator is not None

	def run_test(self,model,**kwargs):
		"""Runs the test and returns a score."""
		self.pre_checks()
		model.run() # Method implementation guaranteed by Runnable capability.  
		model_data = self.get_data(model)
		return self.score(model_data,kwargs)
		
	def get_data(self,model):
		"""Extracts raw data from the model and returns it."""
		model_data = {}
		# Get model_data from the model...
		return model_data

	def get_stats(self,model_data):
		"""Puts stats in a form that the Comparator will understand."""
		model_stats = {key:value for key,value in self.model_data} # This example is trivial.  
		reference_stats = {key:value for key,value in self.reference_data} # This example is trivial.  
		return (model_stats,reference_stats)
	
	