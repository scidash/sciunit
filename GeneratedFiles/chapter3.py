
# coding: utf-8

# ![SciUnit Logo](https://raw.githubusercontent.com/scidash/assets/master/logos/sciunit.png)
# 
# # SciUnit is a framework for validating scientific models by creating experimental-data-driven unit tests.  
# 
# # Chapter 3. Testing with help from the SciUnit standard library
# (or [back to Chapter 2](chapter2.ipynb))

# In[1]:


import sciunit


# ### In this chapter we will use the same toy model in Chapter 1 but write a more interesting test with additional features included in SciUnit. 

# In[2]:


from sciunit.models import ConstModel # One of many dummy models included for illustration.  
const_model_37 = ConstModel(37, name="Constant Model 37")


# Now let's write a test that validates the `observation` and returns more informative `score` type.

# In[3]:


from sciunit.capabilities import ProducesNumber
from sciunit.scores import ZScore # One of many SciUnit score types.  
from sciunit.errors import ObservationError # An exception class raised when a test is instantiated 
                                     # with an invalid observation.
    
class MeanTest(sciunit.Test):
    """Tests if the model predicts 
    the same number as the observation."""   
    
    required_capabilities = (ProducesNumber,) # The one capability required for a model to take this test.  
    score_type = ZScore # This test's 'judge' method will return a BooleanScore.  
    
    def validate_observation(self, observation):
        if type(observation) is not dict:
            raise ObservationError("Observation must be a python dictionary")
        if 'mean' not in observation:
            raise ObservationError("Observation must contain a 'mean' entry")
        
    def generate_prediction(self, model):
        return model.produce_number() # The model has this method if it inherits from the 'ProducesNumber' capability.
    
    def compute_score(self, observation, prediction):
        score = ZScore.compute(observation,prediction) # Compute and return a ZScore object.  
        score.description = ("A z-score corresponding to the normalized location of the observation "
                             "relative to the predicted distribution.")
        return score


# We've done two new things here:
# - The optional `validate_observation` method checks the `observation` to make sure that it is the right type, that it has the right attributes, etc.  This can be used to ensures that the `observation` is exactly as the other core test methods expect.  If we don't provide the right kind of observation:
# ```python
# -> mean_37_test = MeanTest(37, name='=37')
# ObservationError: Observation must be a python dictionary
# ```
# then we get an error.  In contrast, this is what our test was looking for:

# In[4]:


observation = {'mean':37.8, 'std':2.1}
mean_37_test = MeanTest(observation, name='=37')


# - Instead of returning a `BooleanScore`, encoding a `True`/`False` value, we return a `ZScore` encoding a more quantitative summary of the relationship between the observation and the prediction.  When we execute the test:

# In[5]:


score = mean_37_test.judge(const_model_37)


# Then we get a more quantitative summary of the results:

# In[6]:


score.summarize()


# In[7]:


score.describe()

