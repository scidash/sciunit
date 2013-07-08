"""Basic sciunit capabilities"""
import sciunit

class ProducesNumber(sciunit.Capability):
	"""An example capability for producing some generic number."""

	def produce_data(self):
		raise NotImplementedError("Must implement produce_data.")

class Runnable(sciunit.Capability):
	"""The ability to run, i.e. execute, the candidate as a program."""
	
	"""Posix timestamp of the run, to set in run()."""
	run_t = 0
	
	"""Name for the run, to set in run()."""
	run_name = ""
	
	def run(self,name=""):
		"""Run candidate with an optional name."""
		raise NotImplementedError()
  		



