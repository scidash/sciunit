"""
Base class for SciUnit test suites.
"""

import random
from types import MethodType

from .base import SciUnit, TestWeighted
from .utils import log
from .tests import Test
from .models import Model
from .scores import NoneScore
from .scores.collections import ScoreMatrix
from sciunit.scores.collections import ScoreMatrix
from typing import Callable, Dict, List, Optional, Tuple, Type, Union


class TestSuite(SciUnit, TestWeighted):
    """A collection of tests."""

    def __init__(self, tests: List[Test], name: str=None, weights=None, include_models: List[Model]=None,
                 skip_models: List[Model]=None, hooks: dict=None, 
                 optimizer=None):
        """The constructor of TestSuite class.

        Args:
            tests (List[Test]): The list of tests.
            name (str, optional): The name of this test suite. Defaults to None.
            weights (optional): [description]. Defaults to None.
            include_models (List[Model], optional): The list of models. Defaults to None.
            skip_models (List[Model], optional): A list of models that will be skipped. Defaults to None.
            hooks (dict, optional): [description]. Defaults to None.
            optimizer (optional): A function to bind to self.optimize (first argument must be a TestSuite). Defaults to None.
        """

        self.name = name if name else "Suite_%d" % random.randint(0, 1e12)
        if isinstance(tests, dict):
            for key, value in tests.items():
                if not isinstance(value, Test):
                    setattr(self, key, value)
            tests = [test for test in tests.values() if isinstance(test, Test)]
        self.tests = self.assert_tests(tests)
        self.weights_ = [] if not weights else list(weights)
        self.include_models = include_models if include_models else []
        self.skip_models = skip_models if skip_models else []
        self.hooks = hooks
        super(TestSuite, self).__init__()
        if optimizer:
            self.optimize = MethodType(optimizer, self)

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

    def assert_tests(self, tests: Union[List[Test], Test]) -> Union[List[Test], Test]:
        """Check and in some cases fixes the list of tests.

        Args:
            tests (Union[List[Test], Test])): The test suite to be checked and fixed.

        Raises:
            TypeError: `tests` contains a non-Test.
            TypeError: `tests` was not provided with a test or iterable.

        Returns:
            Union[List[Test], Test]): Checked and fixed test(s).
        """

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

    def assert_models(self, models: Union[Model, List[Model]]) -> Union[Tuple[Model], List[Model]]:
        """Check and in some cases fixes the list of models.

        Args:
            models (Union[Model, List[Model]]): The model(s) to be checked and fixed.

        Raises:
            TypeError: `models` contains a non-Test.
            TypeError: `models` Test suite's judge method not provided with a model or iterable."

        Returns:
            Union[Tuple[Model], List[Model]]: Checked and fixed model(s).
        """

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

    def check(self, models: Union[Model, List[Model]], skip_incapable: bool=True, require_extra: bool=False,
              stop_on_error: bool=True) -> ScoreMatrix:
        """Like judge, but without actually running the test.

        Just returns a ScoreMatrix indicating whether each model can take
        each test or not.  A TBDScore indicates that it can, and an NAScore
        indicates that it cannot.

        Args:
            models (Union[Model, List[Model]]): A list of sciunit model or a single sciunit model.
            skip_incapable (bool, optional): Whether to skip incapable models
                                             (or raise an exception). Defaults to True.
            require_extra (bool, optional):  Check to see whether the model implements certain other methods.
                                             Defaults to False.
            stop_on_error (bool, optional):  Whether to raise an Exception if an error
                                             is encountered or just produce an ErrorScore. Defaults to True.

        Returns:
            ScoreMatrix: The ScoreMatrix indicating whether each model can take each test or not.
        """
        models = self.assert_models(models)
        sm = ScoreMatrix(self.tests, models)
        for test in self.tests:
            for model in models:
                sm.loc[model, test] = test.check(model,
                                                 require_extra=require_extra)
        return sm

    def check_capabilities(self, model: Model, skip_incapable: bool=False,
                           require_extra: bool=False) -> list:
        """Check model capabilities against those required by the suite.

        Returns a list of booleans (one for each test in the suite)
        corresponding to 

        Args:
            model (Model): A sciunit model instance.
            skip_incapable (bool, optional): Whether to skip incapable models.
                (or raise an exception). Defaults to False.
            require_extra (bool, optional): Check to see whether the model implements certain other methods. Defaults to False.

        Returns:
            list: A list of booleans that shows whether the required 
                    capabilities of each test are satisfied by the model.
        """
        return [test.check_capabilities(model,
                skip_incapable=skip_incapable, require_extra=require_extra)
                for test in self.tests]

    def judge(self, models: Union[Model, List[Model]],
              skip_incapable: bool=False, stop_on_error: bool=True, deep_error: bool=False) -> ScoreMatrix:
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

    def is_skipped(self, model: Model) -> bool:
        """Indicate whether `model` will be judged or not.

        Args:
            model (Model): A sciunit model instance.

        Returns:
            bool: Whether `model` will be judged or not.
        """
        # Skip if include_models provided and model not found there
        skip = self.include_models and \
            not any([model.is_match(x) for x in self.include_models])
        # Skip if model found in skip_models
        if not skip:
            skip = any([model.is_match(x) for x in self.skip_models])
        return skip

    def judge_one(self, model: Model, test: Test, sm: ScoreMatrix,
                  skip_incapable: bool=True, stop_on_error: bool=True, deep_error: bool=False) -> 'Score':
        """Judge model and put score in the ScoreMatrix.

        Returns:
            Score: The generated score.
        """
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

    def optimize(self, model: Model, *args, **kwargs) -> None:
        """Optimize model parameters to get the best Test Suite scores.

        Args:
            model (Model): A sciunit model instance.

        Raises:
            NotImplementedError: Exception raised if this method is not implemented (not overrided in the subclass).
        """
        raise NotImplementedError(("Optimization not implemented "
                                   "for TestSuite '%s'" % self))

    def set_hooks(self, test: Test, score: 'Score') -> None:
        """Set hook functions to run after each test is executed.

        Args:
            test (Test): A sciunit Test instance.
            score (Score): A sciunit Model instance.
        """
        if self.hooks and test in self.hooks:
            f = self.hooks[test]['f']
            if 'kwargs' in self.hooks[test]:
                kwargs = self.hooks[test]['kwargs']
            else:
                kwargs = {}
            f(test, self.tests, score, **kwargs)

    def set_verbose(self, verbose: bool) -> None:
        """Set the verbosity for logged information about test execution.

        Args:
            verbose (bool): The verbosity to be set for each test.
        """
        for test in self.tests:
            test.verbose = verbose

    @classmethod
    def from_observations(cls, tests_info: List[Tuple["Test", dict]], name: Optional[str]=None):
        """Instantiate a test suite from a set of observations.

        `tests_info` should be a list of tuples containing the test class and
        the observation, e.g. [(TestClass1,obs1),(TestClass2,obs2),...].
        The desired test name may appear as an optional third item in the
        tuple, e.g. (TestClass1,obse1,"my_test").  The same test class may be
        used multiple times, e.g. [(TestClass1,obs1a),(TestClass1,obs1b),...].

        Args:
            tests_info (List[Tuple["Test", dict]]): [description]
            name (Optional[str], optional): The name of this test suite. Defaults to None.

        Returns:
            TestSuite: An instance of TestSuite that contains the tests based on the observations.
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
    
    def __getitem__(self, item: Union[str, int]) -> Test:
        if isinstance(item, int):
            test = self.tests[item]
        else:
            options = [test for test in self.tests if test.name==item]
            if len(options) == 0:
                raise KeyError("No test in this suite with name '%s'" % item)
            elif len(options) >= 2:
                raise KeyError("Multiple tests found in this suite with name '%s'" % item)
            test = options[0]
        return test
    
    def __len__(self) -> int:
        return len(self.tests)

    def __str__(self):
        """Represent the TestSuite instance as a string."""
        return '%s' % self.name
