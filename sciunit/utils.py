"""Utilities for implementation of candidate capabilities
All of these are optional."""
from datetime import now
from sciunit.Capabilities import Runnable

def run(self,**kwargs):
    """Run, i.e. simulate or fit, a candidate model."""
    try:
      	result = self.execute(kwargs)
    except:
      raise RuntimeError("Run Failed.")
    else:
    	self.last_run = now()
    	return result
      
def lookup(self,**kwargs):
    """Lookup for a run with the same metadata in a cache of previous runs."""
    try:
      index = self.metadata.find(kwargs)
    except ValueError:
      raise
    else:
      return self.data[index]

def store(self,run,**kwargs):
    """Store the results of a run and its metadata in a cache of runs."""
    if not hasattr(self.data):
    	self.data = []
    if not hasattr(self.metadata):
    	self.metadata = []
    metadata.append(kwargs)
    data.append(run)
    return run

def cached_run(self,**kwargs):
  """Return a matching cached run, and if it can't be found, run it fresh."""
	try:
		cached = lookup(self,name,**kwargs)
	except ValueError:
		print "No run with these arguments found in the cache."
		run = self.run()
		cached = self.store(self,run,**kwargs)
	return cached

class Cachable(Runnable):
  """The ability to cache the arguments to and results of a candidate run."""
  def lookup(self,run_name="",run_t=0):
    """Lookup a candidate run in the cache."""
    raise NotImplementedError()
  
  def store(self):
    """Store a candidate run in the cache."""
      raise NotImplementedError()




	
	
