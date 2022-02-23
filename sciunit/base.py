"""The base class for many SciUnit objects."""

import sys

PLATFORM = sys.platform
PYTHON_MAJOR_VERSION = sys.version_info.major
if PYTHON_MAJOR_VERSION < 3:  # Python 2
    raise Exception("Only Python 3 is supported")

import hashlib
import inspect
import json
import logging
from pathlib import Path
from typing import Any, List

try:
    import tkinter
except ImportError:
    tkinter = None
try:
    from importlib.metadata import version

    __version__ = version("sciunit")
except:
    __version__ = None

import bs4
import git
from deepdiff import DeepDiff
from git.cmd import Git
from git.exc import GitCommandError, InvalidGitRepositoryError
from git.remote import Remote
from git.repo.base import Repo
import jsonpickle
import jsonpickle.ext.numpy as jsonpickle_numpy
from jsonpickle.handlers import BaseHandler
import numpy as np
import quantities as pq

ipy = "ipykernel" in sys.modules
here = Path(__file__).resolve().parent.name

# Set up generic logger
logger = logging.getLogger("sciunit")
logger.setLevel(logging.WARNING)


class Config(dict):
    """Configuration class for sciunit"""

    def __init__(self, *args, **kwargs):
        self.load()
        super().__init__(*args, **kwargs)

    default = {
        "cmap_high": 218,
        "cmap_low": 38,
        "score_log_level": 1,
        "log_level": logging.INFO,
        "prevalidate": False,
        "cwd": here,
    }

    _path = Path.home() / ".sciunit" / "config.json"

    @property
    def path(self):
        """Guarantees that the requested path will be Path object"""
        return Path(self._path)

    @path.setter
    def path(self, val):
        """Guarantees that any new paths will be Path object"""
        self._path = Path(val)

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key, default=None, update_from_disk=True):
        key = key.lower()
        try:
            val = super().__getitem__(key)
        except KeyError:
            c = self.get_from_disk()
            if default is None:
                val = c[key]
            else:
                val = c.get(key, default)
            if update_from_disk:
                self[key.lower()] = val
        return val

    def set(self, key, val):
        self.__setitem__(key, val)

    def __setitem__(self, key, val):
        key = key.lower()
        super().__setitem__(key, val)

    def get_from_disk(self):
        try:
            with open(self.path, "r") as f:
                c = json.load(f)
        except FileNotFoundError:
            logger.warning(
                "Config file not found at '%s'; creating new one" % self.path
            )
            self.create()
            return self.get_from_disk()
        except json.JSONDecodeError:
            logger.warning(
                "Config file JSON at '%s' was invalid; creating new one" % self.path
            )
            self.create()
            return self.get_from_disk()
        return c

    def create(self, data: dict = None) -> bool:
        """Create a config file that store any data from the user.

        Args:
            data (dict): The data that will be written to the new config file.

        Returns:
            bool: Config file creation is successful
        """
        if not data:
            data = self.default
        success = False
        try:
            config_dir = self.path.parent
            config_dir.mkdir(exist_ok=True, parents=True)
            data["sciunit_version"] = __version__
            with open(self.path, "w") as f:
                f.seek(0)
                f.truncate()
                json.dump(data, f)
            success = True
        except Exception as e:
            logger.warning("Could not create config file: %s" % e)
        return success

    def load(self):
        c = self.get_from_disk()
        for key, val in c.items():
            key = key.lower()
            self[key] = val

    def save(self):
        self.create(data=self)


config = Config()


class Versioned(object):
    """A Mixin class for SciUnit objects.

    Provides a version string based on the Git repository where the model
    is tracked. Provided in part by Andrew Davison in issue #53.
    """

    def get_repo(self, cached: bool = True) -> Repo:
        """Get a git repository object for this instance.

        Args:
            cached (bool, optional): Whether to use cached data. Defaults to True.

        Returns:
            Repo: The git repo for this instance.
        """
        module = sys.modules[self.__module__]
        # We use module.__file__ instead of module.__path__[0]
        # to include modules without a __path__ attribute.
        if hasattr(self.__class__, "_repo") and cached:
            repo = self.__class__._repo
        elif hasattr(module, "__file__"):
            path = Path(module.__file__).resolve()
            try:
                repo = git.Repo(path, search_parent_directories=True)
            except InvalidGitRepositoryError:
                repo = None
        else:
            repo = None
        self.__class__._repo = repo
        return repo

    def get_version(self, cached: bool = True) -> str:
        """Get a git version (i.e. a git commit hash) for this instance.

        Args:
            cached (bool, optional): Whether to use the cached data. Defaults to True.

        Returns:
            str: The git version for this instance.
        """
        if cached and hasattr(self.__class__, "_version"):
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

    def get_remote(self, remote_name: str = "origin", **kwargs) -> Remote:
        """Get a git remote object for this instance.

        Args:
            remote_name (str, optional): The remote Git repo. Defaults to 'origin'.

        Returns:
            Remote: The git remote object for this instance.
        """
        repo = kwargs["repo"] if "repo" in kwargs else self.get_repo()

        if repo is None:
            return None

        if len(repo.remotes) == 0:
            return None

        matching = [r for r in repo.remotes if r.name == remote_name]
        if (len(matching) > 0):
            # => Remote with remote_name
            return matching[0]
        else:
            # => just any first Remote
            return repo.remotes[0]

    def get_remote_url(self, remote: str = "origin", cached: bool = True) -> str:
        """Get a git remote URL for this instance.

        Args:
            remote (str, optional): The remote Git repo. Defaults to 'origin'.
            cached (bool, optional): Whether to use cached data. Defaults to True.

        Raises:
            ex: A Git command error.

        Returns:
            str: The git remote URL for this instance.
        """
        if hasattr(self.__class__, "_remote_url") and cached:
            url = self.__class__._remote_url
        else:
            r = self.get_remote(remote)
            try:
                url = list(r.urls)[0]
            except GitCommandError as ex:
                if "correct access rights" in str(ex):
                    # If ssh is not setup to access this repository
                    cmd = ["git", "config", "--get", "remote.%s.url" % r.name]
                    url = Git().execute(cmd)
                else:
                    raise ex
            except AttributeError:
                url = None
            if url is not None and url.startswith("git@"):
                domain = url.split("@")[1].split(":")[0]
                path = url.split(":")[1]
                url = "http://%s/%s" % (domain, path)
        self.__class__._remote_url = url
        return url

    remote_url = property(get_remote_url)


class SciUnit(Versioned):
    """Abstract base class for models, tests, and scores."""

    def __init__(self):
        """Instantiate a SciUnit object."""
        pass
    
    #: A list of attributes that cannot or should not be pickled.
    #: A URL where the code for this object can be found.
    _url = None

    #: A verbosity level for printing information.
    verbose = 1

    #: A class attribute containing a list of other attributes to be hidden
    # from state calculations
    state_hide = ['hash', 'pickling', 'temp_dir']
    

    def __getstate__(self) -> dict:
        """Copy the object's state from self.__dict__.

        Contains all of the instance attributes. Always uses the dict.copy()
        method to avoid modifying the original state.

        Returns:
            dict: The state of this instance.
        """
        state = dict(inspect.getmembers(self))
        
        state_hide = list(self.get_list_attr_with_bases("state_hide"))
        state_hide += ['state_hide']
        state = {k: v for k, v in state.items()
                 if k not in state_hide
                 and not k.startswith("_")
                 and not inspect.ismethod(v)}
        return state

    def properties(self, keys: list = None, exclude: list = None) -> dict:
        """Get the properties of the instance.

        Args:
            keys (list, optional): If not None, only the properties that are in `keys` will be included in
                                   the return data. Defaults to None.
            exclude (list, optional): The list of properties that will not be included in return data. Defaults to None.

        Returns:
            dict: The dict of properties of the instance.
        """
        exclude = exclude if exclude else []
        exclude += ["state", "id"]
        props = set(self.property_names())
        props -= set(exclude)
        if keys:
            props &= set(keys)
        result = {prop: getattr(self, prop) for prop in props}
        
        return result

    def property_names(self) -> list:
        """Get the raw properties of the instance.

        Returns:
            list: The list of raw properties.
        """
        sciunit_props = set()
        other_props = set()
        bases = list(self.__class__.__bases__)
        bases.append(self.__class__)
        for base in bases:
            class_attrs = dir(base)
            class_props = set([p for p in class_attrs if isinstance(getattr(base, p, None), property)])
            if issubclass(base, SciUnit):   
                sciunit_props |= class_props
            else:
                other_props |= class_props
        state_hide = set(self.get_list_attr_with_bases("state_hide"))
        return list(sciunit_props - other_props - state_hide)

    # @property
    # def state(self) -> dict:
    #    """Get the state of the instance.
    #
    #    Returns:
    #        dict: The state of the instance.
    #    """
    #    return self._state()

    def json(
        self, add_props: bool = True, string: bool = True, unpicklable: bool = False, make_refs: bool = False) -> str:
        """Generate a Json format encoded sciunit instance.

        Args:
            add_props (bool, optional): Whether to add additional properties of the object to the serialization. Defaults to False.
            string (bool, optional): The json content will be `str` type if True, `dict` type otherwise. Defaults to True.

        Returns:
            str: The Json format encoded sciunit instance.
        """
        
        # Possible set jsonpickle handler options
        # This will also apply recursively to all nested objects
        for k, v in locals().items():
            if k != 'self':
                if v is not None:
                    setattr(SciUnitHandler, k, v)
        
        # Do the encoding
        result = jsonpickle.encode(self)

        # Possibly convert back to dict
        if not string:
            result = json.loads(result)
        
        return result

    def diff(self, other, add_props=False):
        s = self.json(add_props=add_props, string=False)
        o = other.json(add_props=add_props, string=False)
        return DeepDiff(s, o)

    def hash(self, serialization: str = None) -> str:
        """A unique numeric identifier of the current state
        of a SciUnit object.

        Returns:
            str: The unique numeric identifier of the current model state.
        """
        if serialization is None:
            serialization = json.dumps(self.json())
        return hashlib.sha224(serialization.encode("latin1")).hexdigest()

    @property
    def _class(self) -> dict:
        url = "" if self.url is None else self.url

        import_path = "{}.{}".format(self.__class__.__module__, self.__class__.__name__)

        return {"name": self.__class__.__name__, "import_path": import_path, "url": url}

    @property
    def url(self) -> str:
        return self._url if self._url else self.remote_url

    def get_list_attr_with_bases(self, attr: str) -> list:
        """Gets a concatenated list of values for an attribute across all parent classes.
        The attribute must be a list."""
        val = set()
        for cls in self.__class__.__mro__:
            val |= set(getattr(cls, attr, []))
        return list(val)


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
            assert all([x >= 0 for x in self.weights_]), "All test weights must be >=0"
            summ = sum(self.weights_)  # Sum of test weights
            assert summ > 0, "Sum of test weights must be > 0"
            weights = [x / summ for x in self.weights_]  # Normalize to sum
        else:
            weights = [1.0 / n for i in range(n)]
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
                    s[key] = "*removed*"
                else:
                    s = s[key]
    return state


def log(*args, **kwargs):
    level = kwargs.get("level", config.get("LOGGING", default=logging.INFO))
    kwargs = {
        k: v
        for k, v in kwargs.items()
        if k in ["exc_info", "stack_info", "stacklevel", "extra"]
    }
    for arg in args:
        arg = strip_html(arg)
        logger.log(level, arg, **kwargs)


def strip_html(html):
    return html if isinstance(html, Exception) else bs4.BeautifulSoup(html, "lxml").text


class SciUnitHandler(BaseHandler):
    """jsonpickle handler for SciUnit objects"""

    add_props = True
    make_refs = False
    unpicklable = False
    string = True
    
    def flatten(self, obj, data):
        """Flatten SciUnit objects"""
        state = obj.__getstate__()
        if self.add_props:
            state.update(obj.properties())
        result = self.context.flatten(state)
        
        if self.unpicklable:
            data['py/object'] = obj.__class__.__name__
            data['py/state'] = result
        else:
            data = self.simplify(result)    
        data['hash'] = obj.hash(serialization=json.dumps(data))
        return data

    def restore(self, data):
        return NotImplemented
    
    def simplify(self, d):
        """Set all 'py/' key:value pairs to their value"""

        if isinstance(d, dict):
            try:
                del d['py/object']
            except:
                pass
            for key in d:
                if key == 'py/object':
                    del d[key]
                elif 'py/' in key:
                    d = d[key]
                    break        
        if isinstance(d, dict):
            for k, v in d.items():
                d[k] = self.simplify(v)
        elif isinstance(d, list):
            for i, x in enumerate(d):
                d[i] = self.simplify(x)
        return d


class QuantitiesHandler(BaseHandler):
    def flatten(self, obj, data):
        """This methods flattens all quantities into a base and units"""
        result = {'base': str(obj.base.tolist()),
                  'units': str(obj._dimensionality)}
        if self.context.unpicklable:
            data['py/state'] = result
        else:
            data = result
        return data
    
    def restore(self, data):
        """If jsonpickle.encode() is called with unpicklable=True then
        this method is used by jsonpickle.decode() to unserialize."""
        try:
            obj = data['py/state']
        except KeyError:
            obj = data
        base = np.array(obj['base'], dtype=np.float64)
        units = obj['units']
        return pq.Quantity(base, units)


class UnitQuantitiesHandler(BaseHandler):
    """Same as above but for unit quantities e.g. Test.units"""
    def flatten(self, obj, data):
        result = str(obj._dimensionality)
        if self.context.unpicklable:
            data['py/state'] = result
        else:
            data = result
        return data
    
    def restore(self, data):
        try:
            units = data['py/state']
        except KeyError:
            units = data
        return pq.unit_registry[units]


# Register serialization handlers
jsonpickle.handlers.register(SciUnit, handler=SciUnitHandler, base=True)
jsonpickle.handlers.register(pq.Quantity, handler=QuantitiesHandler)
jsonpickle.handlers.register(pq.UnitQuantity, handler=UnitQuantitiesHandler)
jsonpickle_numpy.register_handlers()