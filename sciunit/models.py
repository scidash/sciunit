import sciunit
from random import uniform
import json
from datetime import datetime

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

def runcache(func):
	"""A decorator used on a model method which calls the model's run() method
	if the model has not been run using the current arguments or simply sets
	model attributes to match the run results if it has."""  

	def decorate(*args, **kwargs):
		model = args[0] # Assumed to be self.  
		assert hasattr(model,'run'), "Model must have a run method."
		if func.__name__ == 'run': # Run itself.  
			run_args = kw_args
		else: # Any other method.  
			run_args = kwargs['run'] if 'run' in kwargs else {}
		if not hasattr(model.__class__,'cached_runs'):
			model.__class__.cached_runs = {}
		cache = model.__class__.cached_runs
		run_signature = hash(model)+hash(json.dumps(args[1:]))+hash(json.dumps(kwargs))
		if run_signature not in cache:
			run_args = kwargs['run'] if 'run' in kwargs else {}
			model.run(**run_args)
			cache[run_signature] = (datetime.now(),model.__dict__.copy())
		else:
			model.__dict__.update(cache[run_signature][1])
			#print model.x
		return func(*args, **kwargs)
	return decorate

class CachingExample(UniformModel):
	
	def __init__(self, a, b, name=None):
		self.x = None
		super(CachingExample, self).__init__(a, b, name=name)

	@runcache
	def produce_number(self,**kwargs):
		return self.x

	def run(self,**kwargs):
		if 'b' in kwargs:
			self.x = uniform(self.a, self.b)

