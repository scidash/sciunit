import os
import sys
if sys.version_info.major < 3:
    FileNotFoundError = OSError
    json.JSONDecodeError = ValueError
import json
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

from .utils import dict_hash

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
            for key in self.unpicklable:
                if key in state:
                    del state[key]
        return state

    def _state(self, state=None, keys=[], exclude=[]):
        if state is None:
            state = self.__getstate__()
        if keys:
            state = {key:state[key] for key in keys if key in state.keys()}
        if exclude:
            state = {key:state[key] for key in state.keys() if key not in exclude}
        return state

    def _properties(self, keys=[], exclude=[]):
        result = {}
        props = [p for p in dir(self.__class__) \
                 if isinstance(getattr(self.__class__,p),property)]
        exclude += ['state','hash','id']
        for prop in props:
            if prop not in exclude:
                if not keys or prop in keys: 
                    result[prop] = getattr(self,prop)
        return result

    @property
    def state(self):
        return self._state()

    @property
    def hash(self):
        """A unique numeric identifier of the current model state"""
        return dict_hash(self.state)

    def json(self, add_props=False, keys=[], exclude=[]):
        def serialize(obj):
            try:
                s = json.dumps(obj)
            except TypeError:
                state = obj.state
                if add_props:
                    state.update(obj._properties())
                state = self._state(state=state, keys=keys, exclude=exclude)
                s = json.dumps(state, default=serialize)
            return json.loads(s)
        return serialize(self)

    @property
    def _class(self):
        url = getattr(self.__class__,'remote_url','')
        return {'name':self.__class__.__name__,
                'url':url}

    @property
    def id(self):
        return str(self.json)