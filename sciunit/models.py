import sciunit
import sciunit.capabilities
from random import uniform
from datetime import datetime

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

@cypy.intern
class SharedModel(sciunit.Model):
	"""A model that, each time it is instantiated with the same parameters, will
	return the same instance at the same locaiton in memory. 
	Attributes should not be set post-instantiation
	unless the goal is to set those attributes on all models of this class."""
	pass

def runcache(by='value'):
	"""A decorator used on a model method which calls the model's run() method
	if the model has not been run using the current arguments or simply sets
	model attributes to match the run results if it has."""  
	
	def decorate_(func):
		def decorate(*args, **kwargs):
			model = args[0] # Assumed to be self.  
			assert hasattr(model,'run'), "Model must have a run method."
			if func.__name__ == 'run': # Run itself.  
				run_args = kwargs
			else: # Any other method.  
				run_args = kwargs['run'] if 'run' in kwargs else {}
			if not hasattr(model.__class__,'cached_runs'): # If there is no run cache.  
				model.__class__.cached_runs = {} # Create the run cache.  
			cache = model.__class__.cached_runs
			if by == 'value':
				model_dict = {key:value for key,value in list(model.__dict__.items()) \
							  if key[0]!='_'}
				run_signature = hash(repr(model_dict)+repr(run_args)) # Hash key.
			elif by == 'instance':
				run_signature = hash(repr(id(model))+repr(run_args)) # Hash key.
			else:
				raise ValueError("Cache type must be 'value' or 'instance'")
			if run_signature not in cache:
				print("Run with this signature not found in the cache. Running...")
				model.run(**run_args)
				cache[run_signature] = (datetime.now(),model.__dict__.copy())
			else:
				print("Run with this signature found in the cache. Restoring...")
				model.__dict__.update(cache[run_signature][1])
			return func(*args, **kwargs)
		return decorate
	return decorate_

class PersistentUniformModel(UniformModel):
	"""TODO"""
	
	def run(self):
		self._x = uniform(self.a, self.b)

	def produce_number(self):
		return self._x	

class CacheByInstancePersistentUniformModel(PersistentUniformModel):
	"""TODO"""
	
	@runcache(by='instance')
	def produce_number(self):
		return self._x	

class CacheByValuePersistentUniformModel(PersistentUniformModel):
	"""TODO"""
	
	@runcache(by='value')
	def produce_number(self):
		return self._x	

