"""Basic tests for the core of sciunit."""

import sciunit

class ProducesNumber(sciunit.Capability):
	"""An example capability for producing some generic number."""

	def produce_data(self):
		raise NotImplementedError("Must implement produce_data.")

class PositivityTest(sciunit.Test):
	"""Checks whether the model produces a positive value."""

	required_capabilities = (ProducesNumber,)

	def run_test(self, model):
		"""The main testing function."""
		data = model.produce_data()
		return sciunit.BooleanScore(data > 0, {"data": data})

positivity_test = PositivityTest()

class OneModel(sciunit.Model, ProducesNumber):
	"""A model that always produces the number 1 as output."""

	def produce_data(self):
		return 1

one_model = OneModel()

assert sciunit.check_capabilities(positivity_test, one_model)

result = sciunit.run(positivity_test, one_model)

assert isinstance(result, sciunit.TestResult)
assert result.test is positivity_test
assert result.model is one_model
assert result.score.score is True
assert result.score.related_data == {"data": 1}

print "Tests completed successfully."
