import sciunit
from random import uniform

class ConstCandidate(sciunit.Candidate, 
					 sciunit.capabilities.ProducesNumber):
	"""A candidate that always produces a constant number as output."""
	def __init__(self,constant):
		self.constant = constant 
		
	def produce_data(self):
		return self.constant

class UniformCandidate(sciunit.Candidate,
					   sciunit.capabilities.ProducesNumber):
	"""A candidate that always produces a random uniformly distributed number
	in [a,b] as output."""
	def __init__(self,a,b):
		self.value = uniform(a,b)
	
	def produce_data(self):
		return self.value