"""SciUnit score collections, such as arrays and matrices.

These collections allow scores to be organized and visualized
by model, test, or both.
"""

import warnings
from datetime import datetime
from typing import List, Tuple, Union

import bs4
import numpy as np
import pandas as pd
from IPython.display import Javascript, display

from sciunit.base import SciUnit, TestWeighted, config
from sciunit.models import Model
from sciunit.scores import FloatScore, NoneScore, Score
from sciunit.tests import Test


class ScoreArray(pd.Series, SciUnit, TestWeighted):
    """Represents an array of scores derived from a test suite.

    Extends the pandas Series such that items are either
    models subject to a test or tests taken by a model.
    Also displays and compute score summaries in sciunit-specific ways.

    Can use like this, assuming n tests and m models:

    >>> sm[test]

    >>> sm[test]
    (score_1, ..., score_m)
    >>> sm[model]
    (score_1, ..., score_n)
    """

    def __init__(self, tests_or_models, scores=None, weights=None, name=None):
        if scores is None:
            scores = [NoneScore for tom in tests_or_models]
        tests_or_models = self.check_tests_and_models(tests_or_models)
        self.weights_ = [] if not weights else list(weights)
        name = (name or self.__class__.__name__)
        self._name = name  # Necessary for some reason even though
                           # it is also passed to pd.Series constructor
        super(ScoreArray, self).__init__(data=scores, index=tests_or_models,
                                         name=name)
        self.index_type = "tests" if isinstance(tests_or_models[0], Test) else "models"
        setattr(self, self.index_type, tests_or_models)

    state_hide = ['related_data', 'scores', 'norm_scores', 'style', 'plot', 'iat', 'at', 'iloc', 'loc', 'T']
    
    def check_tests_and_models(
        self, tests_or_models: Union[Test, Model]
    ) -> Union[Test, Model]:
        assert all([isinstance(tom, Test) for tom in tests_or_models]) or all(
            [isinstance(tom, Model) for tom in tests_or_models]
        ), "A ScoreArray may be indexed by only test or models"
        return tests_or_models

    def __getitem__(self, item):
        if isinstance(item, str):
            result = self.get_by_name(item)
        else:
            result = super(ScoreArray, self).__getitem__(item)
        return result

    def get_by_name(self, name: str) -> Union[Model, Test]:
        """Get a test or a model by `name`.

        Args:
            name (str): The name of the model or test.

        Raises:
            KeyError: No model or test with name `name`.

        Returns:
            Union[Model, Test]: The model or test found.
        """
        item = None
        for test_or_model in self.index:
            if test_or_model.name == name:
                item = self.__getitem__(test_or_model)
        if item is None:
            raise KeyError("No model or test with name '%s'" % name)
        return item
    
    def __setattr__(self, attr, value):
        self.__dict__[attr] = value

    #def __getattr__(self, name):
    #    if name in self.direct_attrs:
    #        attr = self.apply(lambda x: getattr(x, name))
    #    else:
    #        attr = super(ScoreArray, self).__getattribute__(name)
    #    return attr

    @property
    def related_data(self) -> pd.Series:
        return self.map(lambda x: x.related_data)
    
    @property
    def scores_flat(self) -> list:
        return self.values.tolist()
    
    @property
    def scores(self) -> pd.Series:
        return self.map(lambda x: x.score)
    
    score = scores  # Backwards compatibility
    
    @property
    def norm_scores(self) -> pd.Series:
        """Return the `norm_score` for each test.

        Returns:
            float: The `norm_score` for each test.
        """
        return self.map(lambda x: x.norm_score)

    def mean(self) -> float:
        """Compute a total score for each model over all the tests.

        Uses the `norm_score` attribute, since otherwise direct comparison
        across different kinds of scores would not be possible.

        Returns:
            float: The computed total score for each model over all the tests.
        """

        return np.dot(np.array(self.norm_scores), self.weights)

    def stature(self, test_or_model: Union[Model, Test]) -> int:
        """Compute the relative rank of a model on a test.

        Rank is against other models that were asked to take the test.

        Args:
            test_or_model (Union[Model, Test]): A sciunit model or test instance.
        Returns:
            int: The rank of the model or test instance.
        """
        return self.norm_scores.rank(ascending=False)[test_or_model]
    
    def __getstate__(self):
        return SciUnit.__getstate__(self)


class ScoreMatrix(pd.DataFrame, SciUnit, TestWeighted):
    """Represents a matrix of scores derived from a test suite.
    Extends the pandas DataFrame such that tests are columns and models
    are the index. Also displays and compute score summaries in sciunit-specific ways.

    Can use like this, assuming n tests and m models:

    >>> sm[test]

    >>> sm[test]
    (score_1, ..., score_m)
    >>> sm[model]
    (score_1, ..., score_n)
    """

    def __init__(self, tests, models, scores=None, weights=None, transpose=False):
        """Constructor of ScoreMatrix class

        Args:
            tests (List[Test]): Test instances that will be in the ScoreMatrix
            models (List[Model]): Model instances that will be in the ScoreMatrix
            scores (List[Score], optional): Score instances that will be in the ScoreMatrix. Defaults to None.
            weights ([type], optional): [description]. Defaults to None.
            transpose (bool, optional): [description]. Defaults to False.
        """

        tests, models, scores = self.check_tests_models_scores(tests, models, scores)
        if transpose:
            super(ScoreMatrix, self).__init__(
                data=scores.T, index=tests, columns=models
            )
        else:
            super(ScoreMatrix, self).__init__(data=scores, index=models, columns=tests)
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=(".*Pandas doesn't allow columns " "to be created via a new "),
            )
            self.tests = tests
            self.models = models
            self.weights_ = [] if not weights else list(weights)
            self.transposed = transpose

    show_mean = False
    sortable = False
    colorize = True
    state_hide = ['related_data', 'scores', 'norm_scores', 'style', 'plot', 'iat', 'at', 'iloc', 'loc', 'T']
    
    def check_tests_models_scores(
        self,
        tests: Union[Test, List[Test]],
        models: Union[Model, List[Model]],
        scores: Union[Score, List[Score]],
    ) -> Tuple[List[Test], List[Model], List[Score]]:
        """Check if `tests`, `models`, and `scores` are lists and covert them to lists if they are not.

        Args:
            tests (List[Test]): A sciunit test instance or a list of the test instances.
            models (List[Model]): A sciunit model instance or a list of the model instances.
            scores (List[Score]): A sciunit score instance or a list of the score instances.

        Returns:
            Tuple[List[Test], List[Model], List[Score]]: Tuple of lists of tests, models, and scores instances.
        """
        if isinstance(tests, Test):
            tests = [tests]
        if isinstance(models, Model):
            models = [models]
        if scores is None:
            scores = [[NoneScore for test in tests] for model in models]
        return tests, models, scores

    def __getitem__(self, item):
        if isinstance(item, Test):
            return self.get_test(item)
        elif isinstance(item, Model):
            return self.get_model(item)
        elif isinstance(item, str):
            return self.get_by_name(item)
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            return self.get_group(item)
        raise TypeError("Expected test; model; test,model; or model,test")

    def get_test(self, test: Test) -> ScoreArray:
        """Generate a `ScoreArray` instance with all models and the `test`.

        Args:
            test (Test): The test that will be included in the `ScoreArray` instance.

        Returns:
            ScoreArray: The generated ScoreArray instance.
        """
        return ScoreArray(
            self.models,
            scores=super(ScoreMatrix, self).__getitem__(test),
            weights=self.weights,
            name=test.name,
        )

    def get_model(self, model: Model) -> ScoreArray:
        """Generate a `ScoreArray` instance with all tests and the `model`.

        Args:
            model (Model): The model that will be included in the `ScoreArray` instance.

        Returns:
            ScoreArray: The generated ScoreArray instance.
        """
        return ScoreArray(self.tests,
                          scores=self.loc[model, :],
                          weights=self.weights,
                          name=model.name)

    def get_group(self, x: tuple) -> Union[Model, Test, Score]:
        """[summary]

        Args:
            x (tuple): (test, model) or (model, test).

        Raises:
            TypeError: Expected (test, model) or (model, test).

        Returns:
            Union[Model, Test]: (test, model) or (model, test).
        """
        t = int(bool(self.transposed))
        if isinstance(x[0], Test) and isinstance(x[1], Model):
            result = self.loc[x[1 - t], x[t]]
        elif isinstance(x[1], Test) and isinstance(x[0], Model):
            result = self.loc[x[t], x[1 - t]]
        elif isinstance(x[0], str) or isinstance(x[1], str):
            result = self.__getitem__(x[t]).__getitem__(x[1 - t])
        else:
            raise TypeError("Expected (test, model) or (model, test)")
        return result

    def get_by_name(self, name: str) -> Union[Model, Test]:
        """Get a model or a test from the model or test list by `name`.

        Args:
            name (str): The name of the test or model.

        Raises:
            KeyError: No model or test found by `name`.

        Returns:
            Union[Model, Test]: The model or test found.
        """
        for model in self.models:
            if model.name == name:
                return self.__getitem__(model)
        for test in self.tests:
            if test.name == name:
                return self.__getitem__(test)
        raise KeyError("No model or test with name '%s'" % name)
    
    def __setattr__(self, attr, value):
        self.__dict__[attr] = value

    #def __getattr__(self, name):
    #    if name in self.direct_attrs:
    #        attr = self.applymap(lambda x: getattr(x, name))
    #    else:
    #        attr = super(ScoreMatrix, self).__getattribute__(name)
    #    return attr
    
    @property
    def related_data(self) -> pd.DataFrame:
        return self.applymap(lambda x: x.related_data)
    
    @property
    def scores_flat(self) -> list:
        return self.values.tolist()
    
    @property
    def scores(self) -> pd.DataFrame:
        return self.applymap(lambda x: x.score)
    
    score = scores  # Backwards compatibility

    @property
    def norm_scores(self) -> pd.DataFrame:
        """Get a DataFrame instance that contains norm scores as a matrix.

        Returns:
            DataFrame: The DataFrame instance that contains norm scores as a matrix.
        """
        return self.applymap(lambda x: x.norm_score)

    def stature(self, test: Test, model: Model) -> int:
        """Computes the relative rank of a model on a test compared to other models that were asked to take the test.

        Args:
            test (Test): A sciunit test instance.
            model (Model): A sciunit model instance.

        Returns:
            int: The relative rank of a model on a test
        """

        return self[test].stature(model)

    def copy(self, transpose=False) -> "ScoreMatrix":
        """Get a copy of this ScoreMatrix.

        Returns:
            ScoreMatrix: The transpose of this ScoreMatrix.
        """
        return ScoreMatrix(
            self.tests,
            self.models,
            scores=self.values.T if self.transposed else self.values,
            weights=self.weights,
            transpose=transpose,
        )

    @property
    def T(self) -> "ScoreMatrix":
        """Get transpose of this ScoreMatrix.

        Returns:
            ScoreMatrix: The transpose of this ScoreMatrix.
        """
        return self.copy(transpose=not self.transposed)

    def add_mean(self):
        is_transposed = isinstance(self.index[0], Test)
        if is_transposed:
            sm = self.T
        else:
            sm = self
        tests = [Test({}, name="Mean")] + sm.tests
        mean_scores = [FloatScore(sm[model].mean()) for model in sm.models]
        mean_scores = np.array(mean_scores).reshape(-1, 1)
        scores = np.hstack([mean_scores, sm.values])
        sm_mean = ScoreMatrix(tests=tests, models=sm.models, scores=scores)
        if is_transposed:
            sm_mean = sm_mean.T
        return sm_mean

    def _repr_html_(self):
        sm = self
        if self.show_mean:
            sm = sm.add_mean()
        if self.colorize:
            obj = sm.style.applymap(sm.apply_score_color)
        else:
            obj = super(ScoreMatrix, sm)
        return obj._repr_html_()

    @classmethod
    def apply_score_color(cls, val):
        color = val.color()
        bg_brightness = config.get("score_bg_brightness", 50)
        bg_brightness = [bg_brightness] * 3
        css = "background-color: rgb(%d, %d, %d); " % tuple(bg_brightness)
        css += "color: rgb(%d, %d, %d); text-align: center;" % color
        return css

    def annotate(
        self, df: pd.DataFrame, html: str, show_mean: bool, colorize: bool
    ) -> Tuple[str, int]:
        """[summary]

        Args:
            df (DataFrame): [description]
            html (str): [description]
            show_mean (bool): [description]
            colorize (bool): [description]

        Returns:
            Tuple[str, int]: [description]
        """
        soup = bs4.BeautifulSoup(html, "lxml")
        if colorize:
            self.annotate_headers(soup, df, show_mean)
            self.annotate_body(soup, df, show_mean)
        table = soup.find("table")
        table_id = table["id"] = hash(datetime.now())
        html = str(soup)
        return html, table_id

    def annotate_headers(
        self, soup: bs4.BeautifulSoup, df: pd.DataFrame, show_mean: bool
    ) -> None:
        """[summary]

        Args:
            soup ([type]): [description]
            df (DataFrame): [description]
            show_mean (bool): [description]
        """
        for i, row in enumerate(soup.find("thead").findAll("tr")):
            for j, cell in enumerate(row.findAll("th")[1:]):
                self.annotate_header_cell(cell, df, show_mean, i, j)

    def annotate_header_cell(
        self, cell, df: pd.DataFrame, show_mean: bool, i: int, j: int
    ) -> None:
        """[summary]

        Args:
            cell ([type]): [description]
            df (DataFrame): [description]
            show_mean (bool): [description]
            i (int): [description]
            j (int): [description]
        """
        if show_mean and j == 0:
            self.annotate_mean(cell, df, i)
        else:
            j_ = j - bool(show_mean)
            test = self.tests[j_]
            cell["title"] = test.description
        # Remove ' test' from column headers
        if cell.string[-5:] == " test":
            cell.string = cell.string[:-5]

    def annotate_body(
        self, soup: bs4.BeautifulSoup, df: pd.DataFrame, show_mean: bool
    ) -> None:
        """[summary]

        Args:
            soup (BeautifulSoup): [description]
            df (DataFrame): [description]
            show_mean (bool): [description]
        """
        for i, row in enumerate(soup.find("tbody").findAll("tr")):
            cell = row.find("th")
            if self.transposed:
                cell["title"] = self.tests[i].describe()
            else:
                cell["title"] = self.models[i].describe()
            for j, cell in enumerate(row.findAll("td")):
                self.annotate_body_cell(cell, df, show_mean, i, j)

    def annotate_body_cell(
        self, cell, df: pd.DataFrame, show_mean: bool, i: int, j: int
    ) -> None:
        """[summary]

        Args:
            cell ([type]): [description]
            df (DataFrame): [description]
            show_mean (bool): [description]
            i (int): [description]
            j (int): [description]
        """
        if show_mean and j == 0:
            value = self.annotate_mean(cell, df, i)
        else:
            j_ = j - bool(show_mean)
            if self.transposed:
                score = self[self.models[j_], self.tests[i]]
            else:
                score = self[self.models[i], self.tests[j_]]

            if isinstance(score, pd.Series) and score.ndim == 1:
                score = score[0]
            elif isinstance(score, pd.DataFrame) and score.ndim == 2:
                # Select the first item generated by the iterator.
                score = next(score.items(), None)[1][0]

            value = score.norm_score
            cell["title"] = score.describe(quiet=True)
        rgb = Score.value_color(value)
        cell["style"] = "background-color: rgb(%d,%d,%d);" % rgb

    def annotate_mean(self, cell, df: pd.DataFrame, i: int) -> float:
        """[summary]

        Args:
            cell ([type]): [description]
            df (DataFrame): [description]
            i (int): [description]

        Returns:
            float: [description]
        """
        value = float(df.loc[self.models[i], "Mean"])
        cell["title"] = "Mean sort key value across tests"
        return value

    def dynamify(self, table_id: str) -> None:
        """[summary]

        Args:
            table_id ([type]): [description]
        """
        prefix = "//ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.0"
        js = Javascript(
            "$('#%s').dataTable();" % table_id,
            lib=["%s/jquery.dataTables.min.js" % prefix],
            css=["%s/css/jquery.dataTables.css" % prefix],
        )
        display(js)
        
    def __getstate__(self):
        return SciUnit.__getstate__(self)

