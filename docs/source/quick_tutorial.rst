Quick tutorial
===================

You can read the SciUnit Basic before starting this tutorial for understanding the components of SciUnit.

Creating a Model and a Test instance from scratch
-------------------------------------------------

Let's create a model that can output a constant number.

Importing sciunit at the beginning.

.. code-block:: python
    import sciunit
Creating a subclass of SciUnit Capability class. Each Capability subclass ontains 
one or more unimplemented methods. The Capability subclass can be included in a subclass of 
Test as ``required_capabilities``, and only the models which implements the methods in the 
Capability subclass can be tested by the Test instance.


Here we define a simple capability through which a model can return a single number.

.. code-block:: python
    class ProducesNumCapability(sciunit.Capability):
        """An example capability for producing some generic number."""
        def produce_number(self):
            """The implementation of this method should return a number."""
            raise NotImplementedError("Must implement produce_number.")
And creating a subclass of SciUnit Model. A model we want to test is 
always an instance (with specific model arguments) of a more generic model class.

.. code-block:: python
    class ConstModel(sciunit.Model, ProducesNumCapability):
        """A model that always produces a constant number as output."""
        def __init__(self, constant, name=None):
            self.constant = constant
            super(ConstModel, self).__init__(name=name, constant=constant)
        def produce_number(self):
            return self.constant
Now we have a model and a capability. Let's create a Test class and include the capability in a subclass of Test.
Note that a SciUnit test class must contain:

1. the capabilities a model requires to take the test.

2. the type of score that it will return.

3. an implementation of generate_prediction, which will use the model's capabilities to get some values out of the model.

4. an implementaiton of compute_score, to use the provided observation and the generated prediction to compute a sciunit Score.

.. code-block:: python
    class EqualsTest(sciunit.Test):
        """Tests if the model predicts 
        the same number as the observation."""   
        
        # The one capability required for a model to take this test.
        required_capabilities = (ProducesNumCapability,)  
        # Set the type of score returned by judge method in a Test instance
        score_type = sciunit.scores.BooleanScore
        
        def generate_prediction(self, model):
            return model.produce_number()
        
        def compute_score(self, observation, prediction):
            score = self.score_type(observation['value'] == prediction) # Returns a BooleanScore. 
            score.description = 'Passing score if the prediction equals the observation'
            return score
After defining the subclass of SciUnit Model, we can create an instance of the model that always 
produce number 37.

.. code-block:: python
    const_model_37 = ConstModel(37, name="Constant Model 37")
Suppose we have a observation value, and we want to test if the value match the number predicted (produced) by 
the model instance defined above.

.. code-block:: python
    observation = {'value':37}
    equals_37_test = EqualsTest(observation=observation, name='Equal 37 Test')
Simply call the ``judge`` method of the Test instance with the model instance as an argument.

.. code-block:: python
    score = equals_37_test.judge(model=const_model_37)
Now we got the score instance. 

>>> print(score)
Pass
Printing out the score and we can see that the test was passed.
We can also summarize the score in its entirety, 
printing information about the associated model and test.

>>> score.summarize()
=== Model Constant Model 37 achieved score Pass on test 'Equal 37 Test'. ===
How was that score computed again?

>>> score.describe()
Passing score if the prediction equals the observation
Next, let's create some other test instances that suppose to fail.

.. code-block:: python
    observation = {'value':36}
    equals_36_test = EqualsTest(observation, name='Equal 36 Test')
    observation = {'value':35}
    equals_35_test = EqualsTest(observation, name='Equal 35 Test')
    score1 = equals_36_test.judge(model=const_model_37)
    score2 = equals_36_test.judge(model=const_model_37)
>>> print(score1)
Fail
>>> print(score2)
Fail
We can also put these test instances together in a TestSuite instance. 
The TestSuite also contains a ``judge`` method that can run every Test instance's ``judge`` methods.

.. code-block:: python
    tests = [equals_35_test, equals_36_test, equals_37_test]
    equals_suite = sciunit.TestSuite(tests=tests, name="Equals test suite")
    score_matrix = equals_suite.judge(const_model_37)
    
>>> print(score_matrix)
                  Equal 35 Test Equal 36 Test Equal 37 Test
Constant Model 37          Fail          Fail          Pass
In the result, we can see a 1*3 score matrix that shows the results of each test.
We can create more models and subject those to the test suite to get a more extensive score matrix.

.. code-block:: python
    const_model_36 = ConstModel(36, name='Constant Model 35')
    const_model_35 = ConstModel(35, name='Constant Model 34')
    score_matrix = equals_suite.judge([const_model_36, const_model_35, const_model_37])
    
>>> print(score_matrix)
                  Equal 35 Test Equal 36 Test Equal 37 Test
Constant Model 35          Fail          Pass          Fail
Constant Model 34          Pass          Fail          Fail
Constant Model 37          Fail          Fail          Pass
Now, we can see the result is a 3*3 matrix, and each model pass the corresponding test. 
We can also examine the results only for one of the tests in the suite.

>>> print(score_matrix[equals_35_test])
Constant Model 35    Fail
Constant Model 34    Pass
Constant Model 37    Fail
Name: Equal 35 Test, dtype: object
Or examine the results only for one of the models.  

>>> print(score_matrix[const_model_35])
Equal 35 Test    Pass
Equal 36 Test    Fail
Equal 37 Test    Fail
Name: Constant Model 34, dtype: object
In the next section we'll see how to build slightly more 
sophisticated tests using objects built-in to SciUnit.

Testing with help from the SciUnit standard library
---------------------------------------------------

The ``ConstModel`` class we defined in the last section was included in 
SciUnit package as an example, and we can just import it.

.. code-block:: python
    import sciunit
    from sciunit.models.examples import ConstModel
    from sciunit.capabilities import ProducesNumber
    from sciunit.scores import ZScore # One of many SciUnit score types.  
    from sciunit.errors import ObservationError # An exception class raised when a test 
Let's create the instance of ConstModel.

.. code-block:: python
    const_model_37 = ConstModel(37, name="Constant Model 37")
And a new subclass of SciUnit Test class.

.. code-block:: python
    class MeanTest(sciunit.Test):
        """Tests if the model predicts the same number as the observation."""   
        
        # The one capability required for a model to take this test.
        required_capabilities = (ProducesNumber,)   
        # This test's 'judge' method will return a BooleanScore.
        score_type = ZScore
        
        def validate_observation(self, observation):
            if type(observation) is not dict:
                raise ObservationError("Observation must be a python dictionary")
            if 'mean' not in observation:
                raise ObservationError("Observation must contain a 'mean' entry")
            
        def generate_prediction(self, model):
            return model.produce_number()
        
        def compute_score(self, observation, prediction):
            # Compute and return a ZScore object.
            score = ZScore.compute(observation,prediction)
            score.description = ("A z-score corresponding to the normalized location of the" 
                                "observation relative to the predicted distribution.")
            return score
Compared with the sruff in last section, we've done two new things here:

* The optional ``validate_observation`` method checks the observation to make sure that it is the right type, that it has the right attributes, etc. This can be used to ensures that the observation is exactly as the other core test methods expect. If we don't provide the right kind of observation:

* Instead of returning a BooleanScore, encoding a True/False value, we return a ZScore encoding a more quantitative summary of the relationship between the observation and the prediction.

Let's create a observation and attach it to the MeanTest instance.

.. code-block:: python
    observation = {'mean':37.8, 'std':2.1}
    mean_37_test = MeanTest(observation, name='Equal 37 Test')
    score = mean_37_test.judge(const_model_37)
And let's see what's the result:

>>> score.summarize()
=== Model Constant Model 37 achieved score Z = -0.38 on test 'Equal 37 Test'. ===
>>> score.describe()
A z-score corresponding to the normalized location of theobservation relative to the predicted distribution.

Example of RunnableModel and Backend
------------------------------------

Beside the usual model in previous sections, let's create a model that run a Backend instance to simulate and obtain results.

Firstly, import necessary components from SciUnit package.

.. code-block:: python
    import sciunit, random
    from sciunit.capabilities import Runnable
    from sciunit.scores import BooleanScore
    from sciunit.models import RunnableModel
    from sciunit.models.backends import register_backends, Backend
Let's define subclasses of SciUnit Backend, Test, and Model.

Note that:

1. A SciUnit Backend subclass should implement ``_backend_run`` method.

2. A SciUnit Backend subclass should implement ``run`` method.

.. code-block:: python
    class RandomNumBackend(Backend):
        '''generate a random integer between min and max'''
        def set_run_params(self, **run_params):
            # get min from run_params, if not exist, then 0.
            self.min = run_params.get('min', 0)
            # get max from run_params, if not exist, then self.min + 100.
            self.max = run_params.get('max', self.min + 100)
        def _backend_run(self):
            # generate and return random integer between min and max.
            return random.randint(self.min, self.max)
    class RandomNumModel(RunnableModel):
        """A model that always produces a constant number as output."""
        def run(self):
            self.results = self._backend.backend_run()
    class RangeTest(Test):
        """Tests if the model predicts the same number as the observation."""
        # Default Runnable Capability for RunnableModel
        required_capabilities = (Runnable,)
        # This test's 'judge' method will return a BooleanScore.
        score_type = BooleanScore
        def generate_prediction(self, model):
            model.run()
            return model.results
        def compute_score(self, observation, prediction):
            score = BooleanScore(
                observation['min'] <= prediction and observation['max'] >= prediction
            )
            return score
Let's define the model instance named ``model 1``.

.. code-block:: python
    model = RandomNumModel("model 1")
We must register any backend isntance in order to use it in model instances.

``set_backend`` and ``set_run_params`` methods can help us to set the run-parameters in the model and its backend.

.. code-block:: python
    register_backends({"Random Number": RandomNumBackend})
    model.set_backend("Random Number")
    model.set_run_params(min=1, max=10)
Next, create an observation that requires the generated random integer between 1 and 10 
and a test instance that use the observation and against the model

.. code-block:: python
    observation = {'min': 1, 'max': 10}
    oneToTenTest = RangeTest(observation, "test 1")
    score = oneToTenTest.judge(model)
print the score, and we can see the result.

>>> print(score)
Pass
