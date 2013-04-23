"""Basic tests for the core of sciunit."""

import sciunit

positivity_test = sciunit.tests.PositivityTest()

one_candidate = sciunit.candidates.ConstCandidate(1)

assert sciunit.check_capabilities(positivity_test, one_candidate)

result = sciunit.run(positivity_test, one_candidate)

assert isinstance(result, sciunit.TestResult)
assert result.test is positivity_test
assert result.candidate is one_candidate
assert result.score.score is True
assert result.score.related_data == {"data": 1}

print "Tests completed successfully."
