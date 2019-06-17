"""SciUnit tests live in this module."""

import inspect
import traceback

from sciunit import settings
from sciunit.base import SciUnit
from .capabilities import ProducesNumber
from .models import Model
from .scores import Score, BooleanScore, NoneScore, ErrorScore, TBDScore,\
                    NAScore
from .validators import ObservationValidator, ParametersValidator
from .errors import Error, CapabilityError, ObservationError,\
                    InvalidScoreError, ParametersError
from .utils import dict_combine


class Test(SciUnit):
    """Abstract base class for tests."""

    def __init__(self, observation, name=None, **params):
        """
        Args:
            observation (dict): A dictionary of observed values to parameterize
                                the test.
            name (str, optional): Name of the test instance.
        """
        self.name = name if name else self.__class__.__name__
        assert isinstance(self.name, str), "Test name must be a string"

        if self.description is None:
            self.description = self.__class__.__doc__

        # Use a combination of default_params and params, choosing the latter
        # if there is a conflict.
        self.params = dict_combine(self.default_params, params)
        self.verbose = self.params.pop('verbose', 1)
        self.validate_params(self.params)
        # Compute possible new params from existing params
        self.compute_params()

        self.observation = observation
        if settings['PREVALIDATE']:
            self.validate_observation(self.observation)

        if self.score_type is None or not issubclass(self.score_type, Score):
            raise Error(("The score type '%s' specified for Test '%s' "
                         "is not valid.") % (self.score_type, self.name))

        super(Test, self).__init__()

    name = None
    """The name of the test. Defaults to the test class name."""

    description = None
    """A description of the test. Defaults to the docstring for the class."""

    observation = None
    """The empirical observation that the test is using."""

    default_params = {}
    """A dictionary containing the parameters to the test."""

    score_type = BooleanScore
    """A score type for this test's `judge` method to return."""

    converter = None
    """A conversion to be done on the score after it is computed."""

    observation_schema = None
    """A schema that the observation must adhere to (validated by cerberus).
    Can also be a list of schemas, one of which the observation must match.
    If it is a list, each schema in the list can optionally be named by putting
    (name, schema) tuples in that list."""

    params_schema = None
    """A schema that the params must adhere to (validated by cerberus).
    Can also be a list of schemas, one of which the params must match."""

    def compute_params(self):
        """Compute new params from existing `self.params`.
        Inserts those new params into `self.params`. Use this when some params
        depend upon the values of others.
        Example: `self.params['c'] = self.params['a'] + self.params['b']`
        """
        pass

    def validate_observation(self, observation):
        """Validate the observation provided to the constructor.

        Raises an ObservationError if invalid.
        """
        if not observation:
            raise ObservationError("Observation is missing.")
        if not isinstance(observation, dict):
            raise ObservationError("Observation is not a dictionary.")
        if "mean" in observation and observation["mean"] is None:
            raise ObservationError("Observation mean cannot be 'None'.")
        if self.observation_schema:
            if isinstance(self.observation_schema, list):
                schemas = [x[1] if isinstance(x, tuple) else x
                           for x in self.observation_schema]
                schema = {'oneof_schema': schemas,
                          'type': 'dict'}
            else:
                schema = {'schema': self.observation_schema,
                          'type': 'dict'}
            schema = {'observation': schema}
            v = ObservationValidator(schema, test=self)
            if not v.validate({'observation': observation}):
                raise ObservationError(v.errors)
        return observation

    @classmethod
    def observation_schema_names(cls):
        """Return a list of names of observation schema, if they are set."""
        names = []
        if cls.observation_schema:
            if isinstance(cls.observation_schema, list):
                names = [x[0] if isinstance(x, tuple) else 'Schema %d' % (i+1)
                         for i, x in enumerate(cls.observation_schema)]
        return names

    def validate_params(self, params):
        """Validate the params provided to the constructor.

        Raises an ParametersError if invalid.
        """
        if params is None:
            raise ParametersError("Parameters cannot be `None`.")
        if not isinstance(params, dict):
            raise ParametersError("Parameters are not a dictionary.")
        if self.params_schema:
            if isinstance(self.params_schema, list):
                schema = {'oneof_schema': self.params_schema,
                          'type': 'dict'}
            else:
                schema = {'schema': self.params_schema,
                          'type': 'dict'}
            schema = {'params': schema}
            v = ParametersValidator(schema, test=self)
            if not v.validate({'params': params}):
                raise ParametersError(v.errors)
        return params

    required_capabilities = ()
    """A sequence of capabilities that a model must have in order for the
    test to be run. Defaults to empty."""

    def check_capabilities(self, model, skip_incapable=False,
                           require_extra=False):
        """Check that test's required capabilities are implemented by `model`.

        Raises an Error if model is not a Model.
        Raises a CapabilityError if model does not have a capability.
        """
        if not isinstance(model, Model):
            raise Error("Model %s is not a sciunit.Model." % str(model))
        capable = all([self.check_capability(model, c, skip_incapable,
                                             require_extra)
                       for c in self.required_capabilities])
        return capable

    def check_capability(self, model, c, skip_incapable=False,
                         require_extra=False):
        """Check if `model` has capability `c`.

        Optionally (default:True) raise a `CapabilityError` if it does not.
        """
        capable = c.check(model, require_extra=require_extra)
        if not capable and not skip_incapable:
            raise CapabilityError(model, c)
        return capable

    def condition_model(self, model):
        """Update the model in any way needed before generating the prediction.

        This could include updating parameters such as simulation durations
        that do not define the model but do define experiments performed on
        the model.
        No default implementation.
        """
        pass

    def generate_prediction(self, model):
        """Generate a prediction from a model using the required capabilities.

        No default implementation.
        """
        raise NotImplementedError(("Test %s does not implement "
                                   "generate_prediction.") % str())

    def check_prediction(self, prediction):
        """Check the prediction for acceptable values.

        No default implementation.
        """
        pass

    def compute_score(self, observation, prediction):
        """Generates a score given the observations provided in the constructor
        and the prediction generated by generate_prediction.

        Must generate a score of score_type.
        No default implementation.
        """
        if not hasattr(self, 'score_type') or \
           not hasattr(self.score_type, 'compute'):
            raise NotImplementedError(("Test %s either implements no "
                                       "compute_score method or provides no "
                                       "score_type with a compute method.")
                                      % self.name)
        # After some processing of the observation and the prediction.
        score = self.score_type.compute(observation, prediction)
        return score

    def _bind_score(self, score, model, observation, prediction):
        """Bind some useful attributes to the score."""
        score.model = model
        score.test = self
        score.prediction = prediction
        score.observation = observation
        # Don't let scores share related_data.
        score.related_data = score.related_data.copy()
        self.bind_score(score, model, observation, prediction)

    def bind_score(self, score, model, observation, prediction):
        """For the user to bind additional features to the score."""
        pass

    def check_score_type(self, score):
        """Check that the score is the correct type for this test."""
        if not isinstance(score, (self.score_type, NoneScore, ErrorScore)):
            msg = (("Score for test '%s' is not of correct type. "
                    "The test requires type %s but %s was provided.")
                   % (self.name, self.score_type.__name__,
                      score.__class__.__name__))
            raise InvalidScoreError(msg)

    def _judge(self, model, skip_incapable=True):
        """Generate a score for the model (internal API use only)."""
        # 1.
        self.check_capabilities(model, skip_incapable=skip_incapable)

        # 2.
        prediction = self.generate_prediction(model)
        self.check_prediction(prediction)
        self.last_model = model

        # 3. Validate observation and compute score
        validated = self.validate_observation(self.observation)

        if validated is not None:
            self.observation = validated

        score = self.compute_score(self.observation, prediction)

        if self.converter:
            score = self.converter.convert(score)

        # 4.
        self.check_score_type(score)

        # 5.
        self._bind_score(score, model, self.observation, prediction)

        return score

    def judge(self, model, skip_incapable=False, stop_on_error=True,
              deep_error=False):
        """Generate a score for the provided model (public method).

        Operates as follows:
        1. Checks if the model has all the required capabilities. If it does
           not, and skip_incapable=False, then a `CapabilityError` is raised.
        2. Calls generate_prediction to generate a prediction.
        3. Calls score_prediction to generate a score.
        4. Checks that the score is of score_type, raising an
           InvalidScoreError.
        5. Equips the score with metadata:
           a) A reference to the model, in attribute model.
           b) A reference to the test, in attribute test.
           c) A reference to the prediction, in attribute prediction.
           d) A reference to the observation, in attribute observation.
        6. Returns the score.

        If stop_on_error is true (default), exceptions propagate upward. If
        false, an ErrorScore is generated containing the exception.

        If deep_error is true (not default), the traceback will contain the
        actual code execution error, instead of the content of an ErrorScore.
        """
        if isinstance(model, (list, tuple, set)):
            # If a collection of models is provided
            from .suites import TestSuite
            suite = TestSuite([self], name=self.name)
            # then test them using a one-test suite.
            return suite.judge(model, skip_incapable=skip_incapable,
                               stop_on_error=stop_on_error,
                               deep_error=deep_error)

        if deep_error:
            score = self._judge(model, skip_incapable=skip_incapable)
        else:
            try:
                score = self._judge(model, skip_incapable=skip_incapable)
            except CapabilityError as e:
                score = NAScore(str(e))
                score.model = model
                score.test = self
            except Exception as e:
                e.stack = traceback.format_exc()
                score = ErrorScore(e)
                score.model = model
                score.test = self
        if isinstance(score, ErrorScore) and stop_on_error:
            raise score.score  # An exception.
        return score

    def check(self, model, skip_incapable=True, stop_on_error=True,
              require_extra=False):
        """Check to see if the test can run this model.

        Like judge, but without actually running the test. Just returns a Score
        indicating whether the model can take the test or not.
        """
        try:
            if self.check_capabilities(model, skip_incapable=skip_incapable,
                                       require_extra=require_extra):
                score = TBDScore(None)
            else:
                score = NAScore(None)
        except Exception as e:
            score = ErrorScore(e)
            if stop_on_error:
                raise e
        return score

    def optimize(self, model):
        """Optimize the parameters of the model to get the best score."""
        raise NotImplementedError(("Optimization not implemented "
                                   "for Test '%s'" % self))

    def describe(self):
        """Describe the test in words."""
        result = "No description available"
        if self.description:
            result = "%s" % self.description
        else:
            if self.__doc__:
                s = []
                s += [self.__doc__.strip().replace('\n', '').
                      replace('    ', '')]
                if self.converter:
                    s += [self.converter.description]
                result = '\n'.join(s)
        return result

    @property
    def state(self):
        """Get the frozen (pickled) model state."""
        return self._state(exclude=['last_model'])

    @classmethod
    def is_test_class(cls, other_cls):
        """Return whether `other_cls` is a subclass of this test class."""
        return inspect.isclass(other_cls) and issubclass(other_cls, cls)

    def __str__(self):
        """Return the string representation of the test's name."""
        return '%s' % self.name


class TestM2M(Test):
    """Abstract class for handling tests involving multiple models.

    Enables comparison of model to model predictions, and also against
    experimental reference data (optional).

    Note: 'TestM2M' would typically be used when handling mutliple (>2)
    models, with/without experimental reference data. For single model
    tests, you can use the 'Test' class.
    """

    def __init__(self, observation=None, name=None, **params):
        super(TestM2M, self).__init__(observation, name=name, **params)

    def validate_observation(self, observation):
        """Validate the observation provided to the constructor.

        Note: TestM2M does not compulsorily require an observation
        (i.e. None allowed).
        """
        pass

    def compute_score(self, prediction1, prediction2):
        """Generate a score given the observations provided in the constructor
        and/or the prediction(s) generated by generate_prediction.

        Must generate a score of score_type.

        No default implementation.
        """
        try:
            # After some processing of the observation and/or the prediction(s)
            score = self.score_type.compute(prediction1, prediction2)
            return score
        except Exception:
            raise NotImplementedError(("Test %s either implements no "
                                       "compute_score method or provides no "
                                       "score_type with a compute method.")
                                      % self.name)

    def _bind_score(self, score, prediction1, prediction2, model1, model2):
        """Bind some useful attributes to the score."""
        score.model1 = model1
        score.model2 = model2
        score.test = self
        score.prediction1 = prediction1
        score.prediction2 = prediction2
        # Don't let scores share related_data.
        score.related_data = score.related_data.copy()
        self.bind_score(score, prediction1, prediction2, model1, model2)

    def bind_score(self, score, prediction1, prediction2, model1, model2):
        """For the user to bind additional features to the score."""
        pass

    def _judge(self, prediction1, prediction2, model1, model2=None):
        # TODO: Not sure if below statement is required
        # self.last_model = model

        # 6.
        score = self.compute_score(prediction1, prediction2)
        if self.converter:
            score = self.converter.convert(score)
        # 7.
        if not isinstance(score, (self.score_type, NoneScore, ErrorScore)):
            raise InvalidScoreError(("Score for test '%s' is not of correct "
                                     "type. The test requires type %s but %s "
                                     "was provided.")
                                    % (self.name, self.score_type.__name__,
                                       score.__class__.__name__))
        # 8.
        self._bind_score(score, prediction1, prediction2, model1, model2)

        return score

    def judge(self, models, skip_incapable=False, stop_on_error=True,
              deep_error=False):
        """Generate a score matrix for the provided model(s).

        Operates as follows:
        1. Check if models have been specified as a list/tuple/set.
           If not, raise exception.
        2. Create a list of predictions. If a test observation is provided,
           add it to predictions.
        3. Checks if all models have all the required capabilities. If a model
           does not, then a CapabilityError is raised.
        4. Calls generate_prediction to generate predictions for each model,
           and these are appeneded to the predictions list.
        5. Generate a 2D list as a placeholder for all the scores.
        6. Calls score_prediction to generate scores for each comparison.
        7. Checks that the score is of score_type, raising an
           InvalidScoreError.
        8. Equips the score with metadata:
           a) Reference(s) to the model(s), in attribute model1 (and model2).
           b) A reference to the test, in attribute test.
           c) A reference to the predictions, in attributes prediction1 and
              prediction2.
        9. Returns the score as a Pandas DataFrame.

        If stop_on_error is true (default), exceptions propagate upward. If
        false, an ErrorScore is generated containing the exception.

        If deep_error is true (not default), the traceback will contain the
        actual code execution error, instead of the content of an ErrorScore.
        """

        # 1.
        if not isinstance(models, (list, tuple, set)):
            raise TypeError(("Models must be specified as a list, tuple or "
                             "set. For single model tests, use 'Test' class."))
        else:
            models = list(models)

        # 2.
        predictions = []
        # If observation exists, store it as first element in predictions[]
        if self.observation:
            predictions.append(self.observation)

        for model in models:
            if not isinstance(model, Model):
                raise TypeError(("TestM2M's judge method received a non-Model."
                                 "Invalid model name: '%s'" % model))
            else:
                try:
                    # 3.
                    self.check_capabilities(model,
                                            skip_incapable=skip_incapable)
                    # 4.
                    prediction = self.generate_prediction(model)
                    self.check_prediction(prediction)
                    predictions.append(prediction)
                except CapabilityError as e:
                    raise CapabilityError(model, e.capability,
                                          ("TestM2M's judge method resulted in"
                                           " error for '%s'. Error: '%s'" %
                                           (model, str(e))))
                except Exception as e:
                    raise Exception(("TestM2M's judge method resulted in error"
                                     "for '%s'. Error: '%s'" %
                                     (model, str(e))))

        # 5. 2D list for scores; num(rows) = num(cols) = num(predictions)
        scores = [[NoneScore for x in range(len(predictions))]
                  for y in range(len(predictions))]

        for i in range(len(predictions)):
            for j in range(len(predictions)):
                if not self.observation:
                    model1 = models[i]
                    model2 = models[j]
                elif i == 0 and j == 0:
                    model1 = None
                    model2 = None
                elif i == 0:
                    model1 = models[j-1]
                    model2 = None
                elif j == 0:
                    model1 = models[i-1]
                    model2 = None
                else:
                    model1 = models[i-1]
                    model2 = models[j-1]

                scores[i][j] = self._judge(predictions[i], predictions[j],
                                           model1, model2)
                if isinstance(scores[i][j], ErrorScore) and stop_on_error:
                    raise scores[i][j].score  # An exception.

        # 9.
        from sciunit.scores.collections_m2m import ScoreMatrixM2M
        sm = ScoreMatrixM2M(self, models, scores=scores)
        return sm

    """
    # TODO: see if this needs to be updated and provided:
    def optimize(self, model):
        raise NotImplementedError(("Optimization not implemented "
                                   "for Test '%s'" % self))
    """


class RangeTest(Test):
    """Test if the model generates a number with a certain sign"""

    def __init__(self, observation, name=None):
        super(RangeTest, self).__init__(observation, name=name)

    required_capabilities = (ProducesNumber,)
    score_type = BooleanScore

    def validate_observation(self, observation):
        assert type(observation) in (tuple, list, set)
        assert len(observation) == 2
        assert observation[1] > observation[0]

    def generate_prediction(self, model):
        return model.produce_number()

    def compute_score(self, observation, prediction):
        low = observation[0]
        high = observation[1]
        return self.score_type(low < prediction < high)


class ProtocolToFeaturesTest(Test):
    """Assume that generating a prediction consists of:
    1) Setting up a simulation experiment protocol.
    Depending on the backend, this could include editing simulation parameters
    in memory or editing a model file.  It could include any kind of
    experimental protocol, such as a perturbation.
    2) Running a model (using e.g. RunnableModel)
    3) Extract features from the results

    Developers should not need to manually implement `generate_prediction`, and
    instead should focus on the other three methods here.
    """

    def generate_prediction(self, model):
        run_method = getattr(model, "run", None)
        assert callable(run_method), \
            "Model must have a `run` method to use a ProtocolToFeaturesTest"
        self.setup_protocol(model)
        result = self.get_result(model)
        prediction = self.extract_features(model, result)
        return prediction

    def setup_protocol(self, model):
        return NotImplementedError()

    def get_result(self, model):
        return NotImplementedError()

    def extract_features(self, model, result):
        return NotImplementedError()
