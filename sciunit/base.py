"""The base class for many SciUnit objects."""

import sys

PLATFORM = sys.platform
PYTHON_MAJOR_VERSION = sys.version_info.major
if PYTHON_MAJOR_VERSION < 3:  # Python 2
    raise Exception('Only Python 3 is supported')

import json, git, pickle, hashlib

import numpy as np
import pandas as pd
from pathlib import Path
from git.exc import GitCommandError, InvalidGitRepositoryError
from git.cmd import Git
from git.remote import Remote
from git.repo.base import Repo
from typing import Dict, List, Optional, Tuple, Union, Any
from io import StringIO
try:
    import tkinter
except ImportError:
    tkinter = None

KERNEL = ('ipykernel' in sys.modules)
HERE = Path(__file__).resolve().parent.name


class Versioned(object):
    """A Mixin class for SciUnit objects.

    Provides a version string based on the Git repository where the model
    is tracked. Provided in part by Andrew Davison in issue #53.
    """

    def get_repo(self, cached: bool=True) -> Repo:
        """Get a git repository object for this instance.

        Args:
            cached (bool, optional): Whether to use cached data. Defaults to True.

        Returns:
            Repo: The git repo for this instance.
        """
        module = sys.modules[self.__module__]
        # We use module.__file__ instead of module.__path__[0]
        # to include modules without a __path__ attribute.
        if hasattr(self.__class__, '_repo') and cached:
            repo = self.__class__._repo
        elif hasattr(module, '__file__'):
            path = Path(module.__file__).resolve()
            try:
                repo = git.Repo(path, search_parent_directories=True)
            except InvalidGitRepositoryError:
                repo = None
        else:
            repo = None
        self.__class__._repo = repo
        return repo

    def get_version(self, cached: bool=True) -> str:
        """Get a git version (i.e. a git commit hash) for this instance.

        Args:
            cached (bool, optional): Whether to use the cached data. Defaults to True.

        Returns:
            str: The git version for this instance.
        """
        if cached and hasattr(self.__class__, '_version'):
            version = self.__class__._version
        else:
            repo = self.get_repo()
            if repo is not None:
                head = repo.head
                version = head.commit.hexsha
                if repo.is_dirty():
                    version += "*"
            else:
                version = None
        self.__class__._version = version
        return version
    version = property(get_version)

    def get_remote(self, remote: str='origin') -> Remote:
        """Get a git remote object for this instance.

        Args:
            remote (str, optional): The remote Git repo. Defaults to 'origin'.

        Returns:
            Remote: The git remote object for this instance.
        """
        repo = self.get_repo()
        if repo is not None:
            remotes = {r.name: r for r in repo.remotes}
            r = repo.remotes[0] if remote not in remotes else remotes[remote]
        else:
            r = None
        return r

    def get_remote_url(self, remote: str='origin', cached: bool=True) -> str:
        """Get a git remote URL for this instance.

        Args:
            remote (str, optional): The remote Git repo. Defaults to 'origin'.
            cached (bool, optional): Whether to use cached data. Defaults to True.

        Raises:
            ex: A Git command error.

        Returns:
            str: The git remote URL for this instance.
        """
        if hasattr(self.__class__, '_remote_url') and cached:
            url = self.__class__._remote_url
        else:
            r = self.get_remote(remote)
            try:
                url = list(r.urls)[0]
            except GitCommandError as ex:
                if 'correct access rights' in str(ex):
                    # If ssh is not setup to access this repository
                    cmd = ['git', 'config', '--get', 'remote.%s.url' % r.name]
                    url = Git().execute(cmd)
                else:
                    raise ex
            except AttributeError:
                url = None
            if url is not None and url.startswith('git@'):
                domain = url.split('@')[1].split(':')[0]
                path = url.split(':')[1]
                url = "http://%s/%s" % (domain, path)
        self.__class__._remote_url = url
        return url
    remote_url = property(get_remote_url)


class SciUnit(Versioned):
    """Abstract base class for models, tests, and scores."""

    def __init__(self):
        """Instantiate a SciUnit object."""
        self.unpicklable = []

    #: A list of attributes that cannot or should not be pickled.
    unpicklable = []

    #: A URL where the code for this object can be found.
    _url = None

    #: A verbosity level for printing information.
    verbose = 1

    def __getstate__(self) -> dict:
        """Copy the object's state from self.__dict__.

        Contains all of the instance attributes. Always uses the dict.copy()
        method to avoid modifying the original state.

        Returns:
            dict: The state of this instance.
        """
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        if hasattr(self, 'unpicklable'):
            for key in set(self.unpicklable).intersection(state):
                del state[key]
        return state

    def _state(self, state: dict=None, keys: list=None, 
                exclude: List[str]=None) -> dict:
        """Get the state of the instance.

        Args:
            state (dict, optional): The dict instance that contains a part of state info of this instance. 
                                    Defaults to None.
            keys (list, optional): Some keys of `state`. Values in `state` associated with these keys will be kept 
                                   and others will be discarded. Defaults to None.
            exclude (List[str], optional): The list of keys. Values in `state` that associated with these keys 
                                           will be removed from `state`. Defaults to None.

        Returns:
            dict: The state of the current instance.
        """

        if state is None:
            state = self.__getstate__()
        if keys:
            state = {key: state[key] for key in keys if key in state.keys()}
        if exclude:
            state = {key: state[key] for key in state.keys()
                     if key not in exclude}
            state = deep_exclude(state, exclude)
        return state

    def _properties(self, keys: list=None, exclude: list=None) -> dict:
        """Get the properties of the instance.

        Args:
            keys (list, optional): If not None, only the properties that are in `keys` will be included in 
                                   the return data. Defaults to None.
            exclude (list, optional): The list of properties that will not be included in return data. Defaults to None.

        Returns:
            dict: The dict of properties of the instance.
        """
        result = {}
        props = self.raw_props()
        exclude = exclude if exclude else []
        exclude += ['state', 'id']
        for prop in set(props).difference(exclude):
            if prop == 'properties':
                pass  # Avoid infinite recursion
            elif not keys or prop in keys:
                result[prop] = getattr(self, prop)
        return result

    def raw_props(self) -> list:
        """Get the raw properties of the instance.

        Returns:
            list: The list of raw properties.
        """
        class_attrs = dir(self.__class__)
        return [p for p in class_attrs
                if isinstance(getattr(self.__class__, p, None), property)]

    @property
    def state(self) -> dict:
        """Get the state of the instance.

        Returns:
            dict: The state of the instance.
        """
        return self._state()

    @property
    def properties(self) -> dict:
        """Get the properties of the instance.

        Returns:
            dict: The properties of the instance.
        """
        return self._properties()

    @classmethod
    def dict_hash(cls, d: dict) -> str:
        """SHA224 encoded value of `d`.

        Args:
            d (dict): The dict instance to be SHA224 encoded.

        Returns:
            str: SHA224 encoded value of `d`.
        """
        od = [(key, d[key]) for key in sorted(d)]
        try:
            s = pickle.dumps(od)
        except AttributeError:
            s = json.dumps(od, cls=SciUnitEncoder).encode('utf-8')

        return hashlib.sha224(s).hexdigest()

    @property
    def hash(self) -> str:
        """A unique numeric identifier of the current model state.

        Returns:
            str: The unique numeric identifier of the current model state.
        """
        return self.dict_hash(self.state)

    def json(self, add_props: bool=False, keys: list=None, exclude: list=None, string: bool=True,
             indent: None=None) -> str:
        """Generate a Json format encoded sciunit instance.

        Args:
            add_props (bool, optional): Whether to add additional properties of the object to the serialization. Defaults to False.
            keys (list, optional): Only the keys in `keys` will be included in the json content. Defaults to None.
            exclude (list, optional): The keys in `exclude` will be excluded from the json content. Defaults to None.
            string (bool, optional): The json content will be `str` type if True, `dict` type otherwise. Defaults to True.
            indent (None, optional): If indent is a non-negative integer or string, then JSON array elements and object members 
                                    will be pretty-printed with that indent level. An indent level of 0, negative, or "" will only 
                                    insert newlines. None (the default) selects the most compact representation. Using a positive integer 
                                    indent indents that many spaces per level. If indent is a string (such as "\t"), that string is 
                                    used to indent each level (source: https://docs.python.org/3/library/json.html#json.dump). 
                                    Defaults to None. 

        Returns:
            str: The Json format encoded sciunit instance.
        """
        result = json.dumps(self, cls=SciUnitEncoder,
                            add_props=add_props, keys=keys, exclude=exclude,
                            indent=indent)
        if not string:
            result = json.loads(result)
        return result

    @property
    def _id(self) -> Any:
        return id(self)

    @property
    def _class(self) -> dict:
        url = '' if self.url is None else self.url

        import_path = '{}.{}'.format(
            self.__class__.__module__,
            self.__class__.__name__
            )

        return {'name': self.__class__.__name__,
                'import_path': import_path,
                'url': url}

    @property
    def id(self) -> str:
        return str(self.json)

    @property
    def url(self) -> str:
        return self._url if self._url else self.remote_url


class SciUnitEncoder(json.JSONEncoder):
    """Custom JSON encoder for SciUnit objects."""

    def __init__(self, *args, **kwargs):
        for key in ['add_props', 'keys', 'exclude']:
            if key in kwargs:
                setattr(self.__class__, key, kwargs[key])
                kwargs.pop(key)
        super(SciUnitEncoder, self).__init__(*args, **kwargs)

    def default(self, obj: Any) -> Union[str, dict, list]:
        """Try to encode the object.

        Args:
            obj (Any): Any object to be encoded

        Raises:
            e: Could not JSON serialize the object.

        Returns:
            Union[str, dict, list]: Encoded object.
        """
        try:
            if isinstance(obj, pd.DataFrame):
                o = obj.to_dict(orient='split')
                if isinstance(obj, SciUnit):
                    for old, new in [('data', 'scores'),
                                     ('columns', 'tests'),
                                     ('index', 'models')]:
                        o[new] = o.pop(old)
            elif isinstance(obj, np.ndarray) and len(obj.shape):
                o = obj.tolist()
            elif isinstance(obj, SciUnit):
                state = obj.state
                if self.add_props:
                    state.update(obj.properties)
                o = obj._state(state=state, keys=self.keys,
                               exclude=self.exclude)
            elif isinstance(obj, (dict, list, tuple, str, type(None), bool,
                                  float, int)):
                o = json.JSONEncoder.default(self, obj)
            else:  # Something we don't know how to serialize;
                    # just represent it as truncated string
                o = "%.20s..." % obj
        except Exception as e:
            print("Could not JSON encode object %s" % obj)
            raise e
        return o


class TestWeighted(object):
    """Base class for objects with test weights."""

    @property
    def weights(self) -> List[float]:
        """Returns a normalized list of test weights.

        Returns:
            List[float]: The normalized list of test weights.
        """

        n = len(self.tests)
        if self.weights_:
            assert all([x >= 0 for x in self.weights_]),\
                    "All test weights must be >=0"
            summ = sum(self.weights_)  # Sum of test weights
            assert summ > 0, "Sum of test weights must be > 0"
            weights = [x/summ for x in self.weights_]  # Normalize to sum
        else:
            weights = [1.0/n for i in range(n)]
        return weights


def deep_exclude(state: dict, exclude: list) -> dict:
    """[summary]

    Args:
        state (dict): A dict that represents the state of an instance.
        exclude (list): Attributes that will be marked as 'removed'

    Returns:
        dict: [description]
    """
    tuples = [key for key in exclude if isinstance(key, tuple)]
    s = state
    for loc in tuples:
        for key in loc:
            try:
                s[key]
            except Exception:
                pass
            else:
                if key == loc[-1]:
                    s[key] = '*removed*'
                else:
                    s = s[key]
    return state
