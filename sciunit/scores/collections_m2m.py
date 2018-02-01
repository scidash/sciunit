import pandas as pd

from sciunit.base import SciUnit
from sciunit.models import Model
from sciunit.tests import Test

class ScoreArrayM2M(pd.Series):
    """
    Represents an array of scores derived from TestM2M.
    Extends the pandas Series such that items are either
    models subject to a test or the test itself.
    """

    def __init__(self, test, models, scores):
        items = models if not test.observation else [test]+models
        super(ScoreArrayM2M,self).__init__(data=scores, index=items)

    def __getitem__(self, item):
        if isinstance(item,str):
            for entry in self.index:
                if entry.name == item or "observation" == item.lower():
                    return self.__getitem__(entry)
            raise KeyError("Doesn't match test, 'observation' or any model: '%s'" % item)
        else:
            return super(ScoreArrayM2M,self).__getitem__(item)

    def __getattr__(self, name):
        if name in ['score','sort_keys','related_data']:
            attr = self.apply(lambda x: getattr(x,name))
        else:
            attr = super(ScoreArrayM2M,self).__getattribute__(name)
        return attr

    @property
    def sort_keys(self):
        return self.map(lambda x: x.sort_key)


class ScoreMatrixM2M(pd.DataFrame):
    """
    Represents a matrix of scores derived from TestM2M.
    Extends the pandas DataFrame such that models/observation are both
    columns and the index.
    """

    def __init__(self, test, models, scores):
        if not test.observation:
            items = models
        else:
            # better to have header as "observation" than test.name
            # only affects pandas.DataFrame; not test.name in individual scores
            test.name = "observation"
            items = [test]+models
        super(ScoreMatrixM2M,self).__init__(data=scores, index=items, columns=items)
        self.test = test
        self.models = models

    def __getitem__(self, item):
        if isinstance(item,(Test,Model)):
            return ScoreArrayM2M(self.test, self.models, scores=self.loc[item,:])
        elif isinstance(item,str):
            for model in self.models:
                if model.name == item:
                    return self.__getitem__(model)
            if self.test.name == item or "observation" == item.lower():
                return self.__getitem__(self.test)
            raise KeyError("Doesn't match test, 'observation' or any model: '%s'" % item)
        elif isinstance(item,(list,tuple)) and len(item)==2:
            if isinstance(item[0],(Test,Model)) and isinstance(item[1],(Test,Model)):
                return self.loc[item[0],item[1]]
            elif isinstance(item[0],str):
                return self.__getitem__(item[0]).__getitem__(item[1])
        raise TypeError("Expected test/'observation'; model; test/'observation',model; model,test/'observation'; or model,model")

    def __getattr__(self, name):
        if name in ['score','sort_key','related_data']:
            attr = self.applymap(lambda x: getattr(x,name))
        else:
            attr = super(ScoreMatrixM2M,self).__getattribute__(name)
        return attr

    @property
    def sort_keys(self):
        return self.applymap(lambda x: x.sort_key)