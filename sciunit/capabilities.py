"""Basic sciunit capabilities"""
from sciunit import Capability

class Runnable(Capability):
	"""The ability to run, i.e. execute, the candidate as a program."""
	def run(self,**kwargs):
		"""kwargs contain arguments for candidate execution, e.g. time step."""
		raise NotImplementedError()
  
class Cachable(Runnable):
	"""The ability to cache the arguments to and results of a candidate run."""
	def lookup(self,name,**kwargs):
		"""Lookup a candidate run in the cache."""
		raise NotImplementedError()
	
	def store(self,name,**kwargs):
		"""Store a candidate run in the cache."""
  		raise NotImplementedError()



