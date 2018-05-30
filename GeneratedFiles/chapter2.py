
# coding: utf-8

# ![SciUnit Logo](https://raw.githubusercontent.com/scidash/assets/master/logos/sciunit.png)
# 
# # SciUnit is a framework for validating scientific models by creating experimental-data-driven unit tests.  
# 
# # Chapter 2. Writing a `model` and `test` in SciUnit from scratch
# (or [back to Chapter 1](chapter1.ipynb))

# In[1]:


import sciunit


# ### SciUnit works by making models declare and implement capabilities that tests use to interact with those models.  
# Each `capability` is a subclass of `sciunit.Capability`, and contains one or more unimplemented methods.  Here we define a simple capability through which a model can return a single number.  

# In[2]:


class ProducesNumber(sciunit.Capability):
    """An example capability for producing some generic number."""

    def produce_number(self):
        """The implementation of this method should return a number."""
        raise NotImplementedError("Must implement produce_number.")


# ### SciUnit models subclass `sciunit.Model` as well as each `sciunit.Capability` they aim to implement. 
# Here we create a trivial model class that is instantiated with a single constant.  

# In[3]:


from sciunit.capabilities import ProducesNumber # One of many potential model capabilities.


# In[4]:


class ConstModel(sciunit.Model, 
                 ProducesNumber):
    """A model that always produces a constant number as output."""
    
    def __init__(self, constant, name=None):
        self.constant = constant 
        super(ConstModel, self).__init__(name=name, constant=constant)

    def produce_number(self):
        return self.constant


# ### A `model` we want to test is always an instance (with specific model arguments) of a more generic `model` class.  
# Here we create an instance of `ConstModel` that will always produce the number 37 and give it a name.  

# In[5]:


const_model_37 = ConstModel(37, name="Constant Model 37")


# ### A SciUnit test class must contain:
# 1. the capabilities a model requires to take the test.  
# 2. the type of score that it will return
# 3. an implementation of `generate_prediction`, which will use the model's capabilities to get some values out of the model.
# 4. an implementaiton of `compute_score`, to use the provided observation and the generated prediction to compute a sciunit `Score`.

# In[6]:


from sciunit.scores import BooleanScore # One of several SciUnit score types.  


# In[7]:


class EqualsTest(sciunit.Test):
    """Tests if the model predicts 
    the same number as the observation."""   
    
    required_capabilities = (ProducesNumber,) # The one capability required for a model to take this test.  
    score_type = BooleanScore # This test's 'judge' method will return a BooleanScore.  
    
    def generate_prediction(self, model):
        return model.produce_number() # The model has this method if it inherits from the 'ProducesNumber' capability.
    
    def compute_score(self, observation, prediction):
        score = self.score_type(observation == prediction) # Returns a BooleanScore. 
        score.description = 'Passing score if the prediction equals the observation'
        return score


# ### A SciUnit test is a specific instance of a `test` class, parameterized by the observation (i.e. the empirical data that the `model` aims to recapitulate).  
# Here we create a test instance parameterized by the observation 37.0.  

# In[8]:


equals_37_test = EqualsTest(37, name='=37')


# ### Every test has a `judge` method which executes the test and returns a `score` for the provide model.  
# Here we judge the model we just created using the test we just created.  The `judge` method does a lot of things behind the scenes:  
# 1. It checks to makes sure that your `model` expresses each `capability` required to take the test. It doesn't check to see if they are implemented correctly (how could it know?) but it does check to make sure the `model` at least claims (through inheritance) to express each `capability`. The required capabilities are none other than those in the test's `required_capabilities` attribute. Since `ProducesNumber` is the only required capability, and the `ConstModel` class inherits from the corresponding capability class, that check passes.
# 2. It calls the test's `generate_prediction` method, which uses the model's capabilities to make the model return some quantity of interest, in this case a characteristic number.
# 3. It calls the test's `compute_score` method, which compares the observation the test was instantiated with against the prediction returned in the previous step. This comparison of quantities is cast into a score (in this case, a `BooleanScore`), bound to some `model` output of interest (in this case, the number produces by the `model`), and that `score` object is returned.
# 4. The `score` returned is checked to make sure it is of the type promised in the class definition, i.e. that a `BooleanScore` is returned if a `BooleanScore` is listed in the `score_type` attribute of the `test`.
# 5. The `score` is bound to the `test` that returned it, the `model` that took the `test`, and the prediction and observation that were used to compute it.

# In[9]:


score = equals_37_test.judge(const_model_37)


# ### A score is an object containing information about the result of the test, and the provenance of that result.  
# Printing the `score` just prints a representation of its value (for a `BooleanScore`, `True` has the representation 'Pass')

# In[10]:


score


# We can also summarize the `score` in its entirety, printing information about the associated `model` and `test`.  

# In[11]:


score.summarize()


# How was that score computed again?  

# In[12]:


score.describe()


# ### Several logically related tests can be grouped using a `TestSuite`.  
# These can be instances of the same test class (instantiated with different observations) or instances of different test classes.  Anything tests that you think belongs together can be part of a TestSuite.  A test can be a part of many different suites at once.  

# In[13]:


equals_1_test = EqualsTest(1, name='=1') # Test that model output equals 1.  
equals_2_test = EqualsTest(2, name='=2') # Test that model output equals 2.  

equals_suite = sciunit.TestSuite([equals_1_test, equals_2_test, equals_37_test], name="Equals test suite")


# Now we can test our model using this TestSuite, and display the results.  

# In[14]:


score_matrix = equals_suite.judge(const_model_37)
score_matrix


# We can create more models and subject those to the test suite to get a more extensive score matrix.

# In[15]:


const_model_1 = ConstModel(1, name='Constant Model 1')
const_model_2 = ConstModel(2, name='Constant Model 2')
score_matrix = equals_suite.judge([const_model_1, const_model_2, const_model_37])
score_matrix


# We can also examine the results only for one of the tests in the suite.

# In[16]:


score_matrix[equals_1_test]


# Or examine the results only for one of the models.  

# In[17]:


score_matrix[const_model_2]


# ### In the next section we'll see how to build slightly more sophisticated tests using objects built-in to SciUnit.  
# ### Onto [Chapter 3](chapter3.ipynb)!
