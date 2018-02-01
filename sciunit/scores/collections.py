from datetime import datetime
import warnings

import numpy as np
import pandas as pd
import bs4
from IPython.display import display,HTML,Javascript

from sciunit.base import SciUnit
from sciunit.models import Model
from sciunit.tests import Test
from sciunit.scores import Score,NoneScore

class ScoreArray(pd.Series,SciUnit):
    """
    Represents an array of scores derived from a test suite.
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
        n = len(tests_or_models)
        self.weights = np.ones(n) if weights is None else np.array(weights)
        self.weights /= self.weights.sum() # Normalize
        assert all([isinstance(tom,Test) for tom in tests_or_models]) or \
               all([isinstance(tom,Model) for tom in tests_or_models]), \
               "A ScoreArray may be indexed by only test or models"
        super(ScoreArray,self).__init__(data=scores, index=tests_or_models)
        self.index_type = 'tests' if isinstance(tests_or_models[0],Test) \
                                  else 'models'
        setattr(self,self.index_type,tests_or_models)

    def __getitem__(self, item):
        if isinstance(item,str):
            for test_or_model in self.index:
                if test_or_model.name == item:
                    return self.__getitem__(test_or_model)
            raise KeyError("No model or test with name '%s'" % item)
        else:
            return super(ScoreArray,self).__getitem__(item)

    def __getattr__(self, name):
        if name in ['score','sort_keys','related_data']:
            attr = self.apply(lambda x: getattr(x,name))
        else:
            attr = super(ScoreArray,self).__getattribute__(name)
        return attr
   
    @property   
    def sort_keys(self):
        return self.map(lambda x: x.sort_key)

    def mean(self):
        """Computes a total score for each model over all the tests, 
        using the sort_key, since otherwise direct comparison across different
        kinds of scores would not be possible."""

        return np.dot(np.array(self.sort_keys),self.weights)
        
    def stature(self, test_or_model):
        """Computes the relative rank of a model on a test compared to other models 
        that were asked to take the test."""

        return self.sort_keys.rank(ascending=False)[test_or_model]

#    def view(self):
#        return self


class ScoreMatrix(pd.DataFrame,SciUnit):
    """
    Represents a matrix of scores derived from a test suite.
    Extends the pandas DataFrame such that tests are columns and models
    are the index.  
    Also displays and compute score summaries in sciunit-specific ways.  

    Can use like this, assuming n tests and m models:

    >>> sm[test]

    >>> sm[test]
    (score_1, ..., score_m)
    >>> sm[model]
    (score_1, ..., score_n)
    """

    def __init__(self, tests, models, scores=None, weights=None):
        if isinstance(tests,Test):
            tests = [tests]
        if isinstance(models,Model):
            models = [models]
        if scores is None:
            scores = [[NoneScore for test in tests] for model in models]
        super(ScoreMatrix,self).__init__(data=scores, index=models, columns=tests)
        n = len(tests)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", 
                                    message=(".*Pandas doesn't allow columns "
                                             "to be created via a new "))
            self.tests = tests
            self.models = models
            self.weights = np.ones(n) if weights is None else np.array(weights)
        self.weights /= self.weights.sum()

    show_mean = False
    sortable = False

    def __getitem__(self, item):
        if isinstance(item, Test):
            return ScoreArray(self.models, 
                              scores=super(ScoreMatrix,self).__getitem__(item),
                              weights=self.weights)
        elif isinstance(item, Model):
            return ScoreArray(self.tests, 
                              scores=self.loc[item,:],
                              weights=self.weights)
        elif isinstance(item,str):
            for model in self.models:
                if model.name == item:
                    return self.__getitem__(model)
            for test in self.tests:
                if test.name == item:
                    return self.__getitem__(test)
            raise KeyError("No model or test with name '%s'" % item)
        elif isinstance(item,(list,tuple)) and len(item)==2:
            if isinstance(item[0], Test) and isinstance(item[1], Model):
                return self.loc[item[1],item[0]]
            elif isinstance(item[1], Test) and isinstance(item[0], Model):
                return self.loc[item[0],item[1]]
            elif isinstance(item[0],str):
                return self.__getitem__(item[0]).__getitem__(item[1])
        raise TypeError("Expected test; model; test,model; or model,test")
  
    def __getattr__(self, name):
        if name in ['score','sort_key','related_data']:
            attr = self.applymap(lambda x: getattr(x,name))
        else:
            attr = super(ScoreMatrix,self).__getattribute__(name)
        return attr

    @property   
    def sort_keys(self):
        return self.applymap(lambda x: x.sort_key)
       
    def stature(self, test, model):
        """Computes the relative rank of a model on a test compared to other models 
        that were asked to take the test."""

        return self[test].stature(model)

    def to_html(self, show_mean=None, sortable=None, colorize=True, *args, 
                      **kwargs):
        if show_mean is None:
            show_mean = self.show_mean
        if sortable is None:
            sortable = self.sortable
        df = self.copy()
        if show_mean:
            df.insert(0,'Mean',None)
            df.loc[:,'Mean'] = ['%.3f' % self[m].mean() for m in self.models]
        html = df.to_html(*args, **kwargs) # Pandas method
        
        soup = bs4.BeautifulSoup(html,"lxml")
        if colorize: 
            for i,row in enumerate(soup.find('thead').findAll('tr')):
                for j,cell in enumerate(row.findAll('th')[1:]):
                    if show_mean and j==0:
                        value = float(df.loc[self.models[i],'Mean'])
                        cell['title'] = 'Mean sort key value across tests'
                    else:
                        j_ = j-bool(show_mean)
                        test = self.tests[j_]
                        cell['title'] = test.description
                    # Remove ' test' from column headers
                    if cell.string[-5:] == ' test':
                        cell.string = cell.string[:-5]
            for i,row in enumerate(soup.find('tbody').findAll('tr')):
                cell = row.find('th')
                cell['title'] = self.models[i].describe()
                for j,cell in enumerate(row.findAll('td')):
                    if show_mean and j==0:
                        value = float(df.loc[self.models[i],'Mean'])
                        cell['title'] = 'Mean sort key value across tests'
                    else:
                        j_ = j-bool(show_mean)
                        score = self[self.models[i],self.tests[j_]]
                        value = score.sort_key
                        cell['title'] = score.describe(quiet=True)
                    rgb = Score.value_color(value)
                    cell['style'] = 'background-color: rgb(%d,%d,%d);' % rgb

        table = soup.find('table')
        table_id = table['id'] = hash(datetime.now())
        html = str(soup)
        if sortable:
            prefix = "//ajax.aspnetcdn.com/ajax/jquery.dataTables/1.9.0"
            js = Javascript("$('#%s').dataTable();" % table_id,
                lib=["%s/jquery.dataTables.min.js" % prefix],
                css=["%s/css/jquery.dataTables.css" % prefix])
            display(js)
        return html
    
#    def view(self, *args, **kwargs):
#        html = self.to_html(*args, **kwargs)
#        return HTML(html)

class ScorePanel(pd.Panel,SciUnit):
    def __getitem__(self, item):
        df = super(ScorePanel,self).__getitem__(item)
        assert isinstance(df,pd.DataFrame), \
            "Only Score Matrices can be accessed by attribute from Score Panels"
        score_matrix = ScoreMatrix(models=df.index, tests=df.columns, scores=df)
        return score_matrix 