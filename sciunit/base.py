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
import git
from git.exc import GitCommandError, InvalidGitRepositoryError
from git.cmd import Git

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


class Versioned(object):
    """
    A Mixin class for SciUnit model instances, which provides a version string
    based on the Git repository where the model is tracked.
    Provided in part by Andrew Davison in issue #53.
    """

    def get_repo(self):
        module = sys.modules[self.__module__]
        # We use module.__file__ instead of module.__path__[0]
        # to include modules without a __path__ attribute.
        repo = None
        if hasattr(module,'__file__'):
            path = os.path.realpath(module.__file__)
            try:
                repo = git.Repo(path, search_parent_directories=True)
            except InvalidGitRepositoryError:
                pass
        else:
            repo = None
        return repo
    
    def get_version(self):
        repo = self.get_repo()
        if repo is not None:
            head = repo.head
            version = head.commit.hexsha
            if repo.is_dirty():
                version += "*"
        else:
            version = None
        return version
    version = property(get_version)
    
    def get_remote(self, remote='origin'):
        repo = self.get_repo()
        if repo is not None:
            remotes = {r.name:r for r in repo.remotes}
            r = repo.remotes[0] if remote not in remotes else remotes[remote]
        else:
            r = None
        return r

    def get_remote_url(self, remote='origin'):
        r = self.get_remote(remote)
        try:
            url = list(r.urls)[0]
        except GitCommandError as ex:
            if 'correct access rights' in str(ex):
                # If ssh is not setup to access this repository 
                cmd = ['git','config','--get','remote.%s.url' % r.name]                                                                                           
                url = Git().execute(cmd)
            else:
                raise ex
        except AttributeError:
            url = None
        if url is not None and url.startswith('git@'):
            domain = url.split('@')[1].split(':')[0]
            path = url.split(':')[1]
            url = "http://%s/%s" % (domain,path)
        return url
    remote_url = property(get_remote_url)


class SciUnit(Versioned):
    """Abstract base class for models, tests, and scores."""
    def __init__(self):
        self.unpicklable = [] # Attributes that cannot or should not be pickled.
     
    unpicklable = []
    _url = None
       
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
            state = deep_exclude(state,exclude)
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
        od = [(key,d[key]) for key in sorted(d)]
        try:
            s = pickle.dumps(od)
        except AttributeError:
            s = json.dumps(od,cls=SciUnitEncoder).encode('utf-8')
        return hashlib.sha224(s).hexdigest()

    @property
    def hash(self):
        """A unique numeric identifier of the current model state"""
        return self.dict_hash(self.state)

    def json(self, add_props=False, keys=None, exclude=None, string=True, 
             indent=None):
        #for attr in ['keys','exclude','add_props']:
        #    setattr(SciUnitEncoder,attr,locals()[attr])
        result = json.dumps(self, cls=SciUnitEncoder, 
                            add_props=add_props, keys=keys, exclude=exclude,
                            indent=indent)
        if not string:
            result = json.loads(result)
        return result

    @property
    def _id(self):
        return id(self)

    @property
    def _class(self):
        url = '' if self.url is None else self.url
        return {'name':self.__class__.__name__,
                'url':url}

    @property
    def id(self):
        return str(self.json)

    @property
    def url(self):
        return self._url if self._url else self.remote_url


class SciUnitEncoder(json.JSONEncoder):
    """Custom JSON encoder for SciUnit objects"""

    def __init__(self, *args, **kwargs):
        for key in ['add_props','keys','exclude']:
            if key in kwargs:
                setattr(self.__class__,key,kwargs[key])
                kwargs.pop(key)
        super(SciUnitEncoder,self).__init__(*args,**kwargs)
    
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            o = obj.to_dict(orient='split')
            if isinstance(obj,SciUnit):
                for old,new in [('data','scores'),
                                ('columns','tests'),
                                ('index','models')]:
                    o[new] = o.pop(old)
        elif isinstance(obj,np.ndarray):
            o = obj.tolist()
        elif isinstance(obj,SciUnit):
            state = obj.state
            if self.add_props:
                state.update(obj.properties)
            o = obj._state(state=state, keys=self.keys, exclude=self.exclude)
        elif isinstance(obj,(dict,list,tuple,str,type(None),bool,float,int)):
            o = json.JSONEncoder.default(self, obj)
        else: # Something we don't know how to serialize; 
              # just represent it as truncated string
            o = "%.20s..." % obj
        return o


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


def deep_exclude(state, exclude):
    tuples = [key for key in exclude if isinstance(key,tuple)]
    s = state
    for loc in tuples:
        for key in loc:
            try:
                s[key]
            except:
                pass
            else:
                if key == loc[-1]:
                    s[key] = '*removed*'
                else:
                    s = s[key]
    return state
        