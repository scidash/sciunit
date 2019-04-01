"""
Base class for SciUnit test suites.
"""

import random

from .base import SciUnit, TestWeighted
from .utils import log
from .tests import Test
from .models import Model
from .scores import NoneScore
from .scores.collections import ScoreMatrix


class TestSuite(SciUnit, TestWeighted):
    """A collection of tests."""

    def __init__(self, tests, name=None, weights=None, include_models=None,
                 skip_models=None, hooks=None):
        self.name = name if name else "Suite_%d" % random.randint(0, 1e12)
        self.tests = self.assert_tests(tests)
        self.weights_ = [] if not weights else list(weights)
        self.include_models = include_models if include_models else []
        self.skip_models = skip_models if skip_models else []
        self.hooks = hooks
        super(TestSuite, self).__init__()

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

    def assert_tests(self, tests):
        """Check and in some cases fixes the list of tests."""

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

    def assert_models(self, models):
        """Check and in some cases fixes the list of models."""

        if isinstance(models, Model):
            models = (models,)
        else:
            try:
                for model in models:
                    if not isinstance(model, Model):
                        raise TypeError(("The judge method of Test suite '%s'"
                                         "provided an iterable containing a "
                                         "non-Model '%s'.") % (self, model))
            except TypeError:
                raise TypeError(("Test suite's judge method not provided with "
                                 "a model or iterable."))
        return models

    def check(self, models, skip_incapable=True, require_extra=False,
              stop_on_error=True):
        """Like judge, but without actually running the test.

        Just returns a ScoreMatrix indicating whether each model can take
        each test or not.  A TBDScore indicates that it can, and an NAScore
        indicates that it cannot.
        """
        models = self.assert_models(models)
        sm = ScoreMatrix(self.tests, models)
        for test in self.tests:
            for model in models:
                sm.loc[model, test] = test.check(model,
                                                 require_extra=require_extra)
        return sm

    def check_capabilities(self, model, skip_incapable=False,
                           require_extra=False):
        """Check model capabilities against those required by the suite.

        Returns a list of booleans (one for each test in the suite)
        corresponding to whether the test's required capabilities are satisfied
        by the model.
        """
        return [test.check_capabilities(model,
                skip_incapable=skip_incapable, require_extra=require_extra)
                for test in self.tests]

    def judge(self, models,
              skip_incapable=False, stop_on_error=True, deep_error=False):
        """Judge the provided models against each test in the test suite.

        Args:
            models (list): The models to be judged.
            skip_incapable (bool): Whether to skip incapable models
                (or raise an exception).
            stop_on_error (bool): Whether to raise an Exception if an error
                is encountered or just produce an ErrorScore.
            deep_error (bool): Whether the error message should penetrate
                all the way to the root of the error.

        Returns:
            ScoreMatrix: The resulting scores for all test/model combos.
        """
        models = self.assert_models(models)
        sm = ScoreMatrix(self.tests, models, weights=self.weights)
        for model in models:
            for test in self.tests:
                score = self.judge_one(model, test, sm, skip_incapable,
                                       stop_on_error, deep_error)
                self.set_hooks(test, score)
        return sm

    def is_skipped(self, model):
        """Indicate whether `model` will be judged or not."""
        # Skip if include_models provided and model not found there
        skip = self.include_models and \
            not any([model.is_match(x) for x in self.include_models])
        # Skip if model found in skip_models
        if not skip:
            skip = any([model.is_match(x) for x in self.skip_models])
        return skip

    def judge_one(self, model, test, sm,
                  skip_incapable=True, stop_on_error=True, deep_error=False):
        """Judge model and put score in the ScoreMatrix."""
        if self.is_skipped(model):
            score = NoneScore(None)
        else:
            log('Executing test <i>%s</i> on model <i>%s</i>' % (test, model),
                end=u"... ")
            score = test.judge(model, skip_incapable=skip_incapable,
                               stop_on_error=stop_on_error,
                               deep_error=deep_error)
            log('Score is <a style="color: rgb(%d,%d,%d)">' % score.color()
                + '%s</a>' % score)
        sm.loc[model, test] = score
        return score

    def optimize(self, model):
        """Optimize model parameters to get the best Test Suite scores."""
        raise NotImplementedError(("Optimization not implemented "
                                   "for TestSuite '%s'" % self))

    def set_hooks(self, test, score):
        """Set hook functions to run after each test is executed."""
        if self.hooks and test in self.hooks:
            f = self.hooks[test]['f']
            if 'kwargs' in self.hooks[test]:
                kwargs = self.hooks[test]['kwargs']
            else:
                kwargs = {}
            f(test, self.tests, score, **kwargs)

    def set_verbose(self, verbose):
        """Set the verbosity for logged information about test execution."""
        for test in self.tests:
            test.verbose = verbose

    @classmethod
    def from_observations(cls, tests_info, name=None):
        """Instantiate a test suite from a set of observations.

        `tests_info` should be a list of tuples containing the test class and
        the observation, e.g. [(TestClass1,obs1),(TestClass2,obs2),...].
        The desired test name may appear as an optional third item in the
        tuple, e.g. (TestClass1,obse1,"my_test").  The same test class may be
        used multiple times, e.g. [(TestClass1,obs1a),(TestClass1,obs1b),...].
        """
        tests = []
        for test_info in tests_info:
            test_class, observation = test_info[0:2]
            test_name = None if len(test_info) < 3 else test_info[2]
            assert Test.is_test_class(test_class), \
                "First item in each tuple must be a Test class"
            test = test_class(observation, name=test_name)
            tests.append(test)
        return cls(tests, name=name)

    def __str__(self):
        """Represent the TestSuite instance as a string."""
        return '%s' % self.name
