import sciunit
from random import uniform

class ConstModel(sciunit.Model, 
					 sciunit.capabilities.ProducesNumber):
	"""A model that always produces a constant number as output."""
	def __init__(self,constant):
		self.constant = constant 
		
	def produce_number(self):
		return self.constant

class UniformModel(sciunit.Model,
					   sciunit.capabilities.ProducesNumber):
	"""A model that always produces a random uniformly distributed number
	in [a,b] as output."""
	
	def __init__(self,a,b):
		self.a, self.b = a, b
	
	def produce_number(self):
		return uniform(self.a, self.b)
