"""
The base class for many SciUnit objects
"""

import os
import sys
import json
import pickle
import hashlib

import numpy as np

if sys.version_info.major < 3: # Python 2
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
        exclude += ['state','hash','id']
        for prop in set(props).difference(exclude).intersection:
            if not keys or prop in keys: 
                result[prop] = getattr(self,prop)
        return result

    def raw_props(self):
        return [p for p in dir(self.__class__) \
                if isinstance(getattr(self.__class__,p),property)]

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
        def serialize(obj):
            if isinstance(obj,np.ndarray):
                obj = obj.tolist()
            try:
                s = json.dumps(obj)
            except TypeError:
                state = obj.state
                if add_props:
                    state.update(obj.properties)
                state = self._state(state=state, keys=keys, exclude=exclude)
                s = json.dumps(state, default=serialize)
            return json.loads(s)
        result = serialize(self)
        if string:
            result = json.dumps(result)
        return result

    @property
    def _class(self):
        url = getattr(self.__class__,'remote_url','')
        return {'name':self.__class__.__name__,
                'url':url}

    @property
    def id(self):
        return str(self.json)

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