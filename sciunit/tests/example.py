"""Basic tests for the core of sciunit."""

import sciunit, sciunit.capabilities, sciunit.models, sciunit.scores

class RangeTest(sciunit.Test):
  """Test if the model generates a number with a certain signn"""

  def __init__(self, observation, name=None):
    super(RangeTest, self).__init__(observation,
    								name=name)

  required_capabilities = (sciunit.capabilities.ProducesNumber,)
  score_type = sciunit.scores.BooleanScore
  
  def validate_observation(self, observation):
  	assert type(observation) in (tuple,list,set)
  	assert len(observation)==2
  	assert observation[1]>observation[0]

  def generate_prediction(self, model):
    return model.produce_number()
  
  def compute_score(self, observation, prediction):
    low = observation[0]
    high = observation[1]
    return self.score_type(low < prediction < high)

	
range_2_3_test = RangeTest(observation=[2,3])
one_model = sciunit.models.ConstModel(2.5)
assert range_2_3_test.check_capabilities(one_model)
score = range_2_3_test.judge(one_model)
assert isinstance(score, sciunit.scores.BooleanScore)
assert score.score == True
assert score.test is range_2_3_test
assert score.model is one_model

print("Tests completed successfully.")
