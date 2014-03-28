"""Basic tests for the core of sciunit."""

import sciunit, sciunit.capabilities, sciunit.models, sciunit.scores

class PositivityTest(sciunit.Test):
  def __init__(self, name=None):
    super(PositivityTest, self).__init__(None, name=name)

  required_capabilities = (sciunit.capabilities.ProducesNumber,)
  def generate_prediction(self, model):
    return model.produce_number()

  score_type = sciunit.scores.BooleanScore
  def score_prediction(self, observation, prediction):
    return self.score_type(prediction > 0)

positivity_test = PositivityTest()
one_model = sciunit.models.ConstModel(4)
assert sciunit.check_capabilities(positivity_test, one_model)
score = positivity_test.judge(one_model)
assert isinstance(score, sciunit.scores.BooleanScore)
assert score.score == True
assert score.test is positivity_test
assert score.model is one_model

print "Tests completed successfully."
