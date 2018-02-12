"""
Base class for SciUnit test suites.  
"""

import random

from .base import SciUnit,TestWeighted
from .utils import log
from .tests import Test
from .models import Model
from .scores import NoneScore
from .scores.collections import ScoreMatrix

class TestSuite(SciUnit,TestWeighted):
    """A collection of tests."""

    def __init__(self, tests, name=None, weights=None, include_models=None, 
                 skip_models=None, hooks=None):
        self.name = name if name else "Suite_%d" % random.randint(0,1e12)
        self.tests = self.check_tests(tests)
        self.weights_ = [] if not weights else list(weights)
        self.include_models = include_models if include_models else []
        self.skip_models = skip_models if skip_models else []
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

    def check_tests(self, tests):
        """Checks and in some cases fixes the list of tests."""

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
        return tests

    def check_models(self, models):
        """Checks and in some cases fixes the list of models."""

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
        return models

    def judge(self, models, 
              skip_incapable=False, stop_on_error=True, deep_error=False):
        """Judges the provided models against each test in the test suite.
           Returns a ScoreMatrix.
        """

        models = self.check_models(models)
        sm = ScoreMatrix(self.tests, models, weights=self.weights)
        for model in models:
            for test in self.tests:
                score = self.judge_one(model,test,sm,skip_incapable,
                                       stop_on_error,deep_error)
                self.set_hooks(test,score)
        return sm

    def is_skipped(self, model):
        """Possibly skip model."""

        # Skip if include_models provided and model not found there
        skip = self.include_models and \
               not any([model.is_match(x) for x in self.include_models])
        # Skip if model found in skip_models
        if not skip: 
            skip = any([model.is_match(x) for x in self.skip_models])
        return skip 
        
    def judge_one(self, model, test, sm, 
                  skip_incapable=True, stop_on_error=True, deep_error=False):
        """Judge model and put score in the ScoreMatrix"""
        
        if self.is_skipped(model):
            score = NoneScore(None)
        else:    
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
    def from_observations(cls, tests_info, name=None):
        """Instantiate a test suite with name 'name' and information about tests
        in 'tests_info', as [(TestClass1,obs1),(TestClass2,obs2),...].
        The desired test name may appear as an optional third item in the 
        tuple, e.g. (TestClass1,obse1,"my_test").  The same test class may be 
        used multiple times, e.g. [(TestClass1,obs1a),(TestClass1,obs1b),...].
        """

        tests = []
        for test_info in tests_info:
            test_class,observation = test_info[0:2]
            test_name = None if len(test_info)<3 else test_info[2]
            assert Test.is_test_class(test_class), \
                   "First item in each tuple must be a Test class"
            test = test_class(observation,name=test_name)
            tests.append(test)
        return cls(tests, name=name)

    def __str__(self):
        return '%s' % self.name