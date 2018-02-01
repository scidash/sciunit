import inspect
from fnmatch import fnmatchcase

import numpy as np

from .base import SciUnit
from .utils import log
from .tests import Test
from .models import Model
from .scores import NoneScore
from .scores.collections import ScoreMatrix

class TestSuite(SciUnit):
    """A collection of tests."""
    def __init__(self, name, tests, weights=None, include_models=None, 
                 skip_models=None, hooks=None):
        if name is None:
            raise Error("Suite name required.")
        self.name = name
        if isinstance(tests, Test):
            # Turn singleton test into a sequence
            tests = (tests,)
        else:
            try:
                for test in tests:
                    if not isinstance(test, Test):
                        raise TypeError(("Test suite provided an iterable "
                                         "containing a non-Test."))
            except TypeError:
                raise TypeError(("Test suite was not provided with "
                                 "a test or iterable."))
        self.tests = tests
        n = len(self.tests)
        self.weights = np.ones(n) if weights is None else np.array(weights)
        self.weights /= self.weights.sum() # Normalize
        self.include_models = [] if include_models is None else include_models
        self.skip_models = [] if skip_models is None else skip_models
        self.hooks = hooks
        super(TestSuite,self).__init__()

    name = None
    """The name of the test suite. Defaults to the class name."""

    description = None
    """The description of the test suite. No default."""

    tests = None
    """The sequence of tests that this suite contains."""

    include_models = []
    """List of names or instances of models to judge 
    (all passed to judge are judged by default)."""

    skip_models = []
    """List of names or instances of models to not judge 
    (all passed to judge are judged by default)."""

    def judge(self, models, 
              skip_incapable=False, stop_on_error=True, deep_error=False):
        """Judges the provided models against each test in the test suite.
           Returns a ScoreMatrix.
        """
        if isinstance(models, Model):
            models = (models,)
        else:
            try:
                for model in models:
                    if not isinstance(model, Model):
                        raise TypeError(("Test suite's judge method provided "
                                         "an iterable containing a non-Model."))
            except TypeError:
                raise TypeError(("Test suite's judge method not provided with "
                                 "a model or iterable."))

        sm = ScoreMatrix(self.tests, models, weights=self.weights)
        for model in models:
            skip = self.is_skipped(model)
            for test in self.tests:
                if skip:
                    sm.loc[model,test] = score = NoneScore(None)
                else:
                    score = self.judge_one(model,test,sm,skip_incapable,
                                           stop_on_error,deep_error)
                self.set_hooks(test,score)
        return sm

    def is_skipped(self, model):
        # Possibly skip model
        skip = False # Don't skip by default
        if self.include_models:
            skip = True # Skip unless found in include_models
            for include_model in self.include_models:
                if model == include_model or \
                   (isinstance(include_model,str) and \
                   fnmatchcase(model.name, include_model)):
                   # Found by instance or name
                    skip = False
                    break
        for skip_model in self.skip_models:
            if model == skip_model or \
               (isinstance(skip_model,str) and \
                fnmatchcase(model.name, skip_model)):
                # Found by instance or name
                skip = True
                break
        return skip 
        
    def judge_one(self, model, test, sm, 
                  skip_incapable=True, stop_on_error=True, deep_error=False):
        """Judge model and put score in the ScoreMatrix"""
        log('Executing test <i>%s</i> on model <i>%s</i>' % (test,model), 
            end="... ")
        score = test.judge(model, skip_incapable=skip_incapable, 
                                  stop_on_error=stop_on_error, 
                                  deep_error=deep_error)
        log('Score is <a style="color: rgb(%d,%d,%d)">' % score.color()
          + '%s</a>' % score)
        sm.loc[model, test] = score
        return score

    def optimize(self, model):
        raise NotImplementedError(("Optimization not implemented "
                                   "for TestSuite '%s'" % self))

    def set_hooks(self, test, score):
        if self.hooks and test in self.hooks:
            f = self.hooks[test]['f']
            if 'kwargs' in self.hooks[test]:
                kwargs = self.hooks[test]['kwargs']
            else:
                kwargs = {}
            f(test, self.tests, score, **kwargs)
        

    def set_verbose(self, verbose):
        for test in self.tests:
            test.verbose = verbose

    @classmethod
    def from_observations(cls, name, tests_info):
        """Instantiate a test suite with name 'name' and information about tests
        in 'tests_info', as [(TestClass1,obs1),(TestClass2,obs2),...].
        The desired test name may appear as an optional third item in the 
        tuple, e.g. (TestClass1,obse1,"my_test").  The same test class may be 
        used multiple times, e.g. [(TestClass1,obs1a),(TestClass1,obs1b),...].
        """

        tests = []
        for test_info in tests_info:
            test_class = test_info[0]
            observation = test_info[1]
            test_name = None if len(test_info)<3 else test_info[2]
            assert inspect.isclass(test_class) \
                   and issubclass(test_class, Test), \
                   "First item in each tuple must be a Test class"
            if test_name is not None:
                assert isinstance(test_name,str), "Each test name must be a string"
            tests.append(test_class(observation,name=test_name))
        return cls(name, tests)

    def __str__(self):
        return '%s' % self.name