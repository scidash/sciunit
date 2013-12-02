"""Basic sciunit capabilities"""
import sciunit

class ProducesNumber(sciunit.Capability):
	"""An example capability for producing some generic number."""

	def produce_data(self):
		raise NotImplementedError("Must implement produce_data.")


class ProducesOutputData(sciunit.Capability):
	def get_model_output_data(self):
		"""Extracts data from the model and returns it."""
		return NotImplementedError("")

	def get_model_output_stats(self,output_data):
		"""Puts model stats in a form that a Comparator will understand."""
		return NotImplementedError("")


class Runnable(sciunit.Capability):
	"""The ability to run, i.e. execute, the model as a program."""
	
	"""Posix timestamp of the run, to set in run()."""
	run_t = 0
	
	"""Name for the run, to set in run()."""
	run_name = ""
	
	def run(self,**kwargs):
		"""Run model with an optional name.
		Should set run_t and run_name."""
		raise NotImplementedError()
  		




