"""SciUnit score collections, such as arrays and matrices.

These collections allow scores to be organized and visualized
by model, test, or both.
"""

from datetime import datetime
import warnings

import numpy as np
import pandas as pd
import bs4
from IPython.display import display, Javascript

from sciunit.base import SciUnit, TestWeighted
from sciunit.models import Model
from sciunit.tests import Test
from sciunit.scores import Score, NoneScore
from typing import Union, Tuple, List

class ScoreArray(pd.Series, SciUnit,TestWeighted):
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

    def __init__(self, tests_or_models, scores=None, weights=None):
        if scores is None:
            scores = [NoneScore for tom in tests_or_models]
        tests_or_models = self.check_tests_and_models(tests_or_models)
        self.weights_ = [] if not weights else list(weights)
        super(ScoreArray, self).__init__(data=scores, index=tests_or_models)
        self.index_type = 'tests' if isinstance(tests_or_models[0], Test) \
                          else 'models'
        setattr(self, self.index_type, tests_or_models)

    direct_attrs = ['score', 'norm_scores', 'related_data']

    def check_tests_and_models(self, tests_or_models: Union[Test, Model]) -> Union[Test, Model]:
        assert all([isinstance(tom, Test) for tom in tests_or_models]) or \
               all([isinstance(tom, Model) for tom in tests_or_models]), \
               "A ScoreArray may be indexed by only test or models"
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
            raise KeyError("No model or test with name '%s'" % item)
        return item

    def __getattr__(self, name):
        if name in self.direct_attrs:
            attr = self.apply(lambda x: getattr(x, name))
        else:
            attr = super(ScoreArray, self).__getattribute__(name)
        return attr

    @property
    def norm_scores(self) -> float:
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


class ScoreMatrix(pd.DataFrame, SciUnit, TestWeighted):
    """ Represents a matrix of scores derived from a test suite.
    Extends the pandas DataFrame such that tests are columns and models
    are the index. Also displays and compute score summaries in sciunit-specific ways.

    Can use like this, assuming n tests and m models:

    >>> sm[test]

    >>> sm[test]
    (score_1, ..., score_m)
    >>> sm[model]
    (score_1, ..., score_n)
    """

    def __init__(self, tests, models,
                 scores=None, weights=None, transpose=False):
        """Constructor of ScoreMatrix class

        Args:
            tests (List[Test]): Test instances that will be in the ScoreMatrix
            models (List[Model]): Model instances that will be in the ScoreMatrix
            scores (List[Score], optional): Score instances that will be in the ScoreMatrix. Defaults to None.
            weights ([type], optional): [description]. Defaults to None.
            transpose (bool, optional): [description]. Defaults to False.
        """

        tests, models, scores = self.check_tests_models_scores(
                                                    tests, models, scores)
        if transpose:
            super(ScoreMatrix, self).__init__(data=scores.T, index=tests,
                                              columns=models)
        else:
            super(ScoreMatrix, self).__init__(data=scores, index=models,
                                              columns=tests)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore",
                                    message=(".*Pandas doesn't allow columns "
                                             "to be created via a new "))
            self.tests = tests
            self.models = models
            self.weights_ = [] if not weights else list(weights)
            self.transposed = transpose

    show_mean = False
    sortable = False
    direct_attrs = ['score', 'norm_scores', 'related_data']

    def check_tests_models_scores(self, 
        tests: Union[Test, List[Test]], 
        models: Union[Model, List[Model]], 
        scores: Union[Score, List[Score]]
        ) \
        -> Tuple[List[Test], List[Model], List[Score]]:
        """ Check if `tests`, `models`, and `scores` are lists and covert them to lists if they are not.

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
        return ScoreArray(self.models,
                          scores=super(ScoreMatrix, self).__getitem__(test),
                          weights=self.weights)

    def get_model(self, model: Model) -> ScoreArray:
        """Generate a `ScoreArray` instance with all tests and the `model`.

        Args:
            model (Model): The model that will be included in the `ScoreArray` instance.

        Returns:
            ScoreArray: The generated ScoreArray instance.
        """
        return ScoreArray(self.tests,
                          scores=self.loc[model, :],
                          weights=self.weights)

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
            result = self.loc[x[1-t], x[t]]
        elif isinstance(x[1], Test) and isinstance(x[0], Model):
            result = self.loc[x[t], x[1-t]]
        elif isinstance(x[0], str):
            result = self.__getitem__(x[t]).__getitem__(x[1-t])
        else:
            raise TypeError("Expected test, model or model, test")
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

    def __getattr__(self, name):
        if name in self.direct_attrs:
            attr = self.applymap(lambda x: getattr(x, name))
        else:
            attr = super(ScoreMatrix, self).__getattribute__(name)
        return attr

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

    @property
    def T(self) -> "ScoreMatrix":
        """Get transpose of this ScoreMatrix.

        Returns:
            ScoreMatrix: The transpose of this ScoreMatrix.
        """
        return ScoreMatrix(self.tests, self.models, scores=self.values,
                           weights=self.weights, transpose=True)

    def to_html(self, show_mean: bool=None, sortable: bool=None, colorize: bool=True, *args,
                **kwargs) -> str:
        """Extend Pandas built in `to_html` method for rendering a DataFrame and use it to render a ScoreMatrix.

        Args:
            show_mean (bool, optional): Whether to show the mean value. Defaults to None.
            sortable (bool, optional): [description]. Defaults to None.
            colorize (bool, optional): Whether to colorize the table. Defaults to True.

        Returns:
            str: [description]
        """
        if show_mean is None:
            show_mean = self.show_mean
        if sortable is None:
            sortable = self.sortable
        df = self.copy()
        if show_mean:
            df.insert(0, 'Mean', None)
            df.loc[:, 'Mean'] = ['%.3f' % self[m].mean() for m in self.models]
        html = df.to_html(*args, **kwargs)  # Pandas method
        html, table_id = self.annotate(df, html, show_mean, colorize)
        if sortable:
            self.dynamify(table_id)
        return html

    def annotate(self, df: pd.DataFrame, html: str, show_mean: bool, colorize: bool) -> Tuple[str, int]:
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
        table = soup.find('table')
        table_id = table['id'] = hash(datetime.now())
        html = str(soup)
        return html, table_id

    def annotate_headers(self, soup: bs4.BeautifulSoup, df: pd.DataFrame, show_mean: bool) -> None:
        """[summary]

        Args:
            soup ([type]): [description]
            df (DataFrame): [description]
            show_mean (bool): [description]
        """
        for i, row in enumerate(soup.find('thead').findAll('tr')):
            for j, cell in enumerate(row.findAll('th')[1:]):
                self.annotate_header_cell(cell, df, show_mean, i, j)

    def annotate_header_cell(self, cell, df: pd.DataFrame, show_mean: bool, i: int, j: int) -> None:
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
            j_ = j-bool(show_mean)
            test = self.tests[j_]
            cell['title'] = test.description
        # Remove ' test' from column headers
        if cell.string[-5:] == ' test':
            cell.string = cell.string[:-5]

    def annotate_body(self, soup: bs4.BeautifulSoup, df: pd.DataFrame, show_mean: bool) -> None:
        """[summary]

        Args:
            soup (BeautifulSoup): [description]
            df (DataFrame): [description]
            show_mean (bool): [description]
        """
        for i, row in enumerate(soup.find('tbody').findAll('tr')):
            cell = row.find('th')
            if self.transposed:
                cell['title'] = self.tests[i].describe()
            else:
                cell['title'] = self.models[i].describe()
            for j, cell in enumerate(row.findAll('td')):
                self.annotate_body_cell(cell, df, show_mean, i, j)

    def annotate_body_cell(self, cell, df: pd.DataFrame, show_mean: bool, i: int, j: int) -> None:
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
            j_ = j-bool(show_mean)
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
            cell['title'] = score.describe(quiet=True)
        rgb = Score.value_color(value)
        cell['style'] = 'background-color: rgb(%d,%d,%d);' % rgb

    def annotate_mean(self, cell, df: pd.DataFrame, i: int) -> float:
        """[summary]

        Args:
            cell ([type]): [description]
            df (DataFrame): [description]
            i (int): [description]

        Returns:
            float: [description]
        """
        value = float(df.loc[self.models[i], 'Mean'])
        cell['title'] = 'Mean sort key value across tests'
        return value

    def dynamify(self, table_id: str) -> None:
        """[summary]

        Args:
            table_id ([type]): [description]
        """
        prefix = "//ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.0"
        js = Javascript("$('#%s').dataTable();" % table_id,
                        lib=["%s/jquery.dataTables.min.js" % prefix],
                        css=["%s/css/jquery.dataTables.css" % prefix])
        display(js)
