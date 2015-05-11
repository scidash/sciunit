"""Basic sciunit capabilities"""
import sciunit
import random

from cypy import memoize # Decorator for caching of capability method results.  

class ProducesNumber(sciunit.Capability):
	"""An example capability for producing some generic number."""

	def produce_number(self):
		raise NotImplementedError("Must implement produce_number.")

class UniqueRandomNumberModel(sciunit.Model,ProducesNumber):
    """An example model to ProducesNumber."""

    def produce_number(self):
        """Each call to this method will produce a different random number."""
        return random.random()

class RepeatedRandomNumberModel(sciunit.Model,ProducesNumber):
    """An example model to demonstrate ProducesNumber with cypy.lazy."""

    @memoize
    def produce_number(self):
        """Each call to this method will produce the same random number as
        was returned in the first call, ensuring reproducibility and
        eliminating computational overhead."""
        return random.random()

