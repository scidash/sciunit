import sciunit
from random import uniform

class ConstModel(sciunit.Model, 
					 sciunit.capabilities.ProducesNumber):
	"""A model that always produces a constant number as output."""
	def __init__(self,constant):
		self.constant = constant 
		
	def produce_data(self):
		return self.constant

class UniformModel(sciunit.Model,
					   sciunit.capabilities.ProducesNumber):
	"""A model that always produces a random uniformly distributed number
	in [a,b] as output."""
	def __init__(self,a,b):
		self.value = uniform(a,b)
	
	def produce_data(self):
		return self.value