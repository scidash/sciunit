"""Score collections for direct comparison of models against other models."""

import warnings

import pandas as pd

from sciunit.models import Model
from sciunit.tests import Test
from typing import List, Any, Union, Tuple

class ScoreArrayM2M(pd.Series):
    """
    Represents an array of scores derived from TestM2M.
    Extends the pandas Series such that items are either
    models subject to a test or the test itself.

    Attributes:
        index ([type]): [description]
    """

    def __init__(self, test: Test, models: List[Model], scores: List['sciunit.scores.Score']):
        items = models if not test.observation else [test]+models
        super(ScoreArrayM2M, self).__init__(data=scores, index=items)

    def __getitem__(self, item: Union[str, callable]) -> Any:
        if isinstance(item, str):
            result = self.get_by_name(item)
        else:
            result = super(ScoreArrayM2M, self).__getitem__(item)
        return result

    def __getattr__(self, name: str) -> Any:
        if name in ['score', 'norm_scores', 'related_data']:
            attr = self.apply(lambda x: getattr(x, name))
        else:
            attr = super(ScoreArrayM2M,self).__getattribute__(name)
        return attr

    def get_by_name(self, name: str) -> str:
        """Get item (can be a model, observation, or test) in `index` by name.

        Args:
            name (str): name of the item.

        Raises:
            KeyError: Item not found.

        Returns:
            Any: Item found.
        """
        for entry in self.index:
            if entry.name == name or name.lower() == "observation":
                return self.__getitem__(entry)
        raise KeyError(("Doesn't match test, 'observation' or "
                        "any model: '%s'") % name)

    @property
    def norm_scores(self) -> pd.Series:
        """A series of norm scores.

        Returns:
            Series: A series of norm scores.
        """
        return self.map(lambda x: x.norm_score)


class ScoreMatrixM2M(pd.DataFrame):
    """
    Represents a matrix of scores derived from TestM2M.
    Extends the pandas DataFrame such that models/observation are both
    columns and the index.
    """

    def __init__(self, test: Test, models: List[Model], scores: List['sciunit.scores.Score']):
        if not test.observation:
            items = models
        else:
            # better to have header as "observation" than test.name
            # only affects pandas.DataFrame; not test.name in individual scores
            test.name = "observation"
            items = [test]+models
        super(ScoreMatrixM2M, self).__init__(data=scores, index=items,
                                             columns=items)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore",
                                    message=(".*Pandas doesn't allow columns "
                                             "to be created via a new "))
            self.test = test
            self.models = models

    def __getitem__(self, item: Union[Tuple[Test, Model], str, Tuple[list, tuple]]) -> Any:
        if isinstance(item, (Test, Model)):
            result = ScoreArrayM2M(self.test, self.models,
                                   scores=self.loc[item, :])
        elif isinstance(item, str):
            result = self.get_by_name(item)
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            result = self.get_group(item)
        else:
            raise TypeError(("Expected test/'observation'; model; "
                             "test/'observation',model; "
                             "model,test/'observation'; or model,model"))
        return result

    def get_by_name(self, name: str) -> Union[Model, Test]:
        """Get the model or test from the `models` or `tests` by name.

        Args:
            name (str): The name of the model or test.

        Raises:
            KeyError: Raise an exception if there is not a model or test named `name`.

        Returns:
            Union[Model, Test]: The test or model found.
        """
        for model in self.models:
            if model.name == name:
                return self.__getitem__(model)
            if self.test.name == name or name.lower() == "observation":
                return self.__getitem__(self.test)
        raise KeyError(("Doesn't match test, 'observation' or "
                        "any model: '%s'") % name)

    def get_group(self, x: list) -> Any:
        """[summary]

        Args:
            x (list): [description]

        Raises:
            TypeError: [description]

        Returns:
            Any: [description]
        """
        if isinstance(x[0], (Test, Model)) and isinstance(x[1], (Test, Model)):
            return self.loc[x[0], x[1]]
        elif isinstance(x[0], str):
            return self.__getitem__(x[0]).__getitem__(x[1])
        raise TypeError("Expected test/model pair")

    def __getattr__(self, name: str) -> Any:
        if name in ['score', 'norm_score', 'related_data']:
            attr = self.applymap(lambda x: getattr(x, name))
        else:
            attr = super(ScoreMatrixM2M, self).__getattribute__(name)
        return attr

    @property
    def norm_scores(self) -> pd.DataFrame:
        """Get a pandas DataFrame instance that contains norm scores.

        Returns:
            DataFrame: A pandas DataFrame instance that contains norm scores.
        """
        return self.applymap(lambda x: x.norm_score)
