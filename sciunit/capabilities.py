"""Basic sciunit capabilities"""
import sciunit

class ProducesNumber(sciunit.Capability):
	"""An example capability for producing some generic number."""

	def produce_number(self):
		raise NotImplementedError("Must implement produce_data.")
