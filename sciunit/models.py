from random import uniform
from datetime import datetime

import sciunit
import sciunit.capabilities
from sciunit.utils import class_intern,method_cache
import cypy

class ConstModel(sciunit.Model, 
					 sciunit.capabilities.ProducesNumber):
	"""A model that always produces a constant number as output."""
	
	def __init__(self, constant, name=None):
		self.constant = constant 
		super(ConstModel, self).__init__(name=name, constant=constant)
		
	def produce_number(self):
		return self.constant

class UniformModel(sciunit.Model,
					   sciunit.capabilities.ProducesNumber):
	"""A model that always produces a random uniformly distributed number
	in [a,b] as output."""
	
	def __init__(self, a, b, name=None):
		self.a, self.b = a, b
		super(UniformModel, self).__init__(name=name, a=a, b=b)
	
	def produce_number(self):
		return uniform(self.a, self.b)

@class_intern
class SharedModel(sciunit.Model):
	"""A model that, each time it is instantiated with the same parameters, will
	return the same instance at the same locaiton in memory. 
	Attributes should not be set post-instantiation
	unless the goal is to set those attributes on all models of this class."""
	pass

class PersistentUniformModel(UniformModel):
	"""TODO"""
	
	def run(self):
		self._x = uniform(self.a, self.b)

	def produce_number(self):
		return self._x	

class CacheByInstancePersistentUniformModel(PersistentUniformModel):
	"""TODO"""
	
	@method_cache(by='instance',method='run')
	def produce_number(self):
		return self._x	

class CacheByValuePersistentUniformModel(PersistentUniformModel):
	"""TODO"""
	
	@method_cache(by='value',method='run')
	def produce_number(self):
		return self._x	
