"""Basic tests for the core of sciunit."""

import sciunit

class ProducesNumber(sciunit.Capability):
	"""An example capability for producing some generic number."""

	def produce_data(self):
		raise NotImplementedError("Must implement produce_data.")

class PositivityTest(sciunit.Test):
	"""Checks whether the candidate produces a positive value."""

	required_capabilities = (ProducesNumber,)

	def run_test(self, candidate):
		"""The main testing function."""
		data = candidate.produce_data()
		return sciunit.BooleanScore(data > 0, {"data": data})

positivity_test = PositivityTest()

class OneCandidate(sciunit.Candidate, ProducesNumber):
	"""A candidate that always produces the number 1 as output."""

	def produce_data(self):
		return 1

one_candidate = OneCandidate()

assert sciunit.check_capabilities(positivity_test, one_candidate)

result = sciunit.run(positivity_test, one_candidate)

assert isinstance(result, sciunit.TestResult)
assert result.test is positivity_test
assert result.candidate is one_candidate
assert result.score.score is True
assert result.score.related_data == {"data": 1}

print "Tests completed successfully."
