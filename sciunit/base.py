"""
The base class for many SciUnit objects
"""

import os
import sys
import json
import pickle
import hashlib

import numpy as np
import pandas as pd

PYTHON_MAJOR_VERSION = sys.version_info.major

if PYTHON_MAJOR_VERSION < 3: # Python 2
    from StringIO import StringIO
    try:
        import Tkinter as tkinter
    except ImportError:
        pass # Handled in the importing modules's fix_display()
    FileNotFoundError = OSError
    json.JSONDecodeError = ValueError
else:
    from io import StringIO
    import tkinter
    FileNotFoundError = FileNotFoundError

KERNEL = ('ipykernel' in sys.modules)
LOGGING = True
HERE = os.path.dirname(os.path.realpath(__file__))

class SciUnit(object):
    """Abstract base class for models, tests, and scores."""
    def __init__(self):
        self.unpicklable = [] # Attributes that cannot or should not be pickled.
     
    unpicklable = []
       
    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        if hasattr(self,'unpicklable'):
            for key in set(self.unpicklable).intersection(state):
                del state[key]
        return state

    def _state(self, state=None, keys=None, exclude=None):
        if state is None:
            state = self.__getstate__()
        if keys:
            state = {key:state[key] for key in keys if key in state.keys()}
        if exclude:
            state = {key:state[key] for key in state.keys() if key not in exclude}
        return state

    def _properties(self, keys=None, exclude=None):
        result = {}
        props = self.raw_props()
        exclude = exclude if exclude else []
        exclude += ['state','id']
        for prop in set(props).difference(exclude):
            if prop == 'properties':
                pass # Avoid infinite recursion
            elif not keys or prop in keys:  
                result[prop] = getattr(self,prop)
        return result

    def raw_props(self):
        class_attrs = dir(self.__class__)
        return [p for p in class_attrs \
                if isinstance(getattr(self.__class__,p,None),property)]

    @property
    def state(self):
        return self._state()

    @property
    def properties(self):
        return self._properties()

    @classmethod
    def dict_hash(cls,d):
        pickled = pickle.dumps([(key,d[key]) for key in sorted(d)])
        return hashlib.sha224(pickled).hexdigest()

    @property
    def hash(self):
        """A unique numeric identifier of the current model state"""
        return self.dict_hash(self.state)

    def json(self, add_props=False, keys=None, exclude=None, string=True):
        for attr in ['keys','exclude','add_props']:
            setattr(SciUnitEncoder,attr,locals()[attr])
        result = json.dumps(self,cls=SciUnitEncoder)
        if not string:
            result = json.loads(result)
        return result

    @property
    def _class(self):
        url = getattr(self.__class__,'remote_url','')
        return {'name':self.__class__.__name__,
                'url':url}

    @property
    def id(self):
        return str(self.json)


class SciUnitEncoder(json.JSONEncoder):
    """Custom JSON encoder for SciUnit objects"""

    add_props = False
    keys = None
    exclude = None
    
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            d = obj.to_dict(orient='split')
            for old,new in [('data','scores'),
                                ('columns','tests'),('index','models')]:
                    d[new] = d.pop(old)
            return d
        elif isinstance(obj,np.ndarray):
            return obj.tolist()
        elif isinstance(obj,SciUnit):
            state = obj.state
            if self.add_props:
                state.update(obj.properties)
            state = obj._state(state=state, 
                               keys=self.keys, exclude=self.exclude)
            return state
        return json.JSONEncoder.default(self, obj)


class TestWeighted(object):
    """Base class for objects with test weights."""

    @property
    def weights(self):
        """Returns a normalized list of test weights."""

        n = len(self.tests)
        if self.weights_:
            assert all([x>=0 for x in self.weights_]), "All test weights must be >=0"
            summ = sum(self.weights_) # Sum of test weights
            assert summ > 0, "Sum of test weights must be > 0"
            weights = [x/summ for x in self.weights_] # Normalize to sum
        else:
            weights = [1.0/n for i in range(n)]
        return weights