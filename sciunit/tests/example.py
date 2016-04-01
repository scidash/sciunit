"""Basic tests for the core of sciunit."""

import sciunit, sciunit.capabilities, sciunit.models, sciunit.scores

class PositivityTest(sciunit.Test):
  def __init__(self, name=None):
    super(PositivityTest, self).__init__(None, name=name)

  required_capabilities = (sciunit.capabilities.ProducesNumber,)
  def generate_prediction(self, model, verbose=False):
    return model.produce_number()

  score_type = sciunit.scores.BooleanScore
  def compute_score(self, observation, prediction, verbose=False):
    return self.score_type(prediction > 0)

positivity_test = PositivityTest()
one_model = sciunit.models.ConstModel(4)
assert positivity_test.check_capabilities(one_model)
score = positivity_test.judge(one_model)
assert isinstance(score, sciunit.scores.BooleanScore)
assert score.score == True
assert score.test is positivity_test
assert score.model is one_model

print("Tests completed successfully.")
