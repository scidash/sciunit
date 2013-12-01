"""SciUnit tests live in this module."""
import sciunit
import sciunit.capabilities

class ComparatorTest(sciunit.Test):
	"""A standard test class that encourages the use of Comparators."""
	def __init__(self,comparator):
		self.comparator = comparator()
		"""Comparator from sciunit.Comparators."""


class PositivityTest(sciunit.Test):
	"""Checks whether the model produces a positive value."""

	required_capabilities = (sciunit.capabilities.ProducesNumber,)

	def _judge(self, model):
		"""The main testing function."""
		data = model.produce_data()
		return BooleanScore(data > 0, {"data": data})


class StandardTest(ComparatorTest):
	"""The first test class that will be useful."""
	
	def __init__(self,reference_data,model_args,comparator):
		"""reference_data are summary statistics of reference data.
		model_args are arguments used by the model to run 
		or fit itself."""
		super(StandardTest,self).__init__(comparator)
		self.reference_data.update(reference_data) # Store reference data. 
		self.model_args.update(model_args) # Store model arguments.  
		self.required_capabilities += (sciunit.capabilities.Runnable,)
		
	def pre_checks(self):
		"""Checks that the test has everything it needs to run properly."""
		assert sciunit.Comparator in self.comparator.__class__.mro()

	def _judge(self,model):
		"""Runs the test and returns a score."""
		self.pre_checks()
		model.run()
		# Run implementation guaranteed by Runnable capability.  
		model_data = self.get_model_data(model)
		return self.generate_score(model_data)
		
	def get_model_data(self,model):
		"""Extracts raw data from the model using Capabilities and returns it."""
		model_data = {}
		# Get model_data from the model...
		return model_data

	def get_model_stats(self,model_data):
		"""Puts model stats in a form that the Comparator will understand."""
		return {key:value for key,value in model_data.items()} # This example is trivial.  
		
	def get_reference_stats(self):
		"""Puts reference stats in a form that the Comparator will understand."""
		return {key:value for key,value in self.reference_data.items()} # This example is trivial.  
		
	def generate_score(self,model_data):
		"""Generate a score using some Comparator applied to the data."""
		model_stats = self.get_model_stats(model_data)
		reference_stats = self.get_reference_stats()
		score = self.comparator.compare(model_stats,reference_stats)
		score.model_data = model_data
		score.reference_data = self.reference_data
		return score
	