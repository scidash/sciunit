import sciunit
from random import uniform

class ConstModel(sciunit.Model, 
					 sciunit.capabilities.ProducesNumber):
	"""A model that always produces a constant number as output."""
	def __init__(self, constant, name=None):
		self.constant = constant 
		super(ConstModel, self).__init__(name=name)
		
	def produce_number(self):
		return self.constant

class UniformModel(sciunit.Model,
					   sciunit.capabilities.ProducesNumber):
	"""A model that always produces a random uniformly distributed number
	in [a,b] as output."""
	
	def __init__(self, a, b, name=None):
		self.a, self.b = a, b
		super(UniformModel, self).__init__(name=name)
	
	def produce_number(self):
		return uniform(self.a, self.b)
