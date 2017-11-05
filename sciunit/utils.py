"""
Utility functions for SciUnit.
"""

from __future__ import print_function
import os
import sys
import subprocess
import warnings
import pkgutil
import importlib
import pickle
import hashlib
from datetime import datetime
try: # Python 3
    import tkinter
except ImportError: # Python 2
    try:
        import Tkinter as tkinter
    except ImportError:
        pass    #handled in fix_display()
import inspect
from io import TextIOWrapper,StringIO
try:
    import unittest.mock
    mock = True
except ImportError:
    mock = False
mock = False # mock is probably obviated by the unittest -b flag.

import nbformat
import nbconvert
from nbconvert.preprocessors import ExecutePreprocessor
from quantities.dimensionality import Dimensionality
from quantities.quantity import Quantity
import cypy
import git
from git.exc import GitCommandError
from git.cmd import Git

PRINT_DEBUG_STATE = False # printd does nothing by default.


def printd_set(state):
    global PRINT_DEBUG_STATE
    PRINT_DEBUG_STATE = (state is True)


def printd(*args, **kwargs):
    global PRINT_DEBUG_STATE
    if PRINT_DEBUG_STATE:
        print(*args, **kwargs)
        return True
    else:
        return False


def assert_dimensionless(value):
    """
    Tests for dimensionlessness of input.
    If input is dimensionless but expressed as a Quantity, it returns the
    bare value.  If it not, it raised an error.
    """
    if isinstance(value,Quantity):
        value = value.simplified
        if value.dimensionality == Dimensionality({}):
            value = value.base.item()
        else:
            raise TypeError("Score value %s must be dimensionless" % value)
    return value


class NotebookTools(object):

    def __init__(self, *args, **kwargs):
        super(NotebookTools,self).__init__(*args, **kwargs)
        self.fix_display()

    path = '' # Relative path to the parent directory of the notebook.

    def get_path(self, file):
        class_path = inspect.getfile(self.__class__)
        parent_path = os.path.dirname(class_path)
        path = os.path.join(parent_path,self.path,file)
        return os.path.realpath(path)

    def fix_display(self):
        """If this is being run on a headless system the Matplotlib
        backend must be changed to one that doesn't need a display."""

        try:
            root = tkinter.Tk()
        except (tkinter.TclError, NameError): # If there is no display.
            try:
                import matplotlib as mpl
            except ImportError:
                pass
            else:
                "Setting matplotlib backend to Agg"
                mpl.use('Agg')

    def load_notebook(self, name):
        """Loads a notebook file into memory."""

        with open(self.get_path('%s.ipynb'%name)) as f:
            nb = nbformat.read(f, as_version=4)
        return nb,f

    def run_notebook(self, nb, f):
        """Runs a loaded notebook file."""

        if (sys.version_info >= (3, 0)):
            kernel_name = 'python3'
        else:
            kernel_name = 'python2'
        ep = ExecutePreprocessor(timeout=600, kernel_name=kernel_name)
        try:
            out = ep.preprocess(nb, {'metadata': {'path': '.'}})
        except CellExecutionError:
            out = None
            msg = 'Error executing the notebook "%s".\n\n' % f.name
            msg += 'See notebook "%s" for the traceback.' % f.name
            print(msg)
            raise
        finally:
            nbformat.write(nb, f)

    def execute_notebook(self, name):
        """Loads and then runs a notebook file."""

        warnings.filterwarnings("ignore", category=DeprecationWarning)
        nb,f = self.load_notebook(name)
        self.run_notebook(nb,f)
        self.assertTrue(True)

    def convert_notebook(self, name):
        """Converts a notebook into a python file."""

        #subprocess.call(["jupyter","nbconvert","--to","python",
        #                self.get_path("%s.ipynb"%name)])
        exporter = nbconvert.exporters.python.PythonExporter()
        file_path = self.get_path("%s.ipynb"%name)
        code = exporter.from_filename(file_path)[0]
        self.write_code(name, code)
        self.clean_code(name, ['get_ipython'])

    def convert_and_execute_notebook(self, name):
        """Converts a notebook into a python file and then runs it."""

        self.convert_notebook(name)
        code = self.read_code(name)
        exec(code,globals())

    def read_code(self, name):
        """Reads code from a python file called 'name'"""

        file_path = self.get_path('%s.py'%name)
        with open(file_path) as f:
            code = f.read()
        return code

    def write_code(self, name, code):
        """Writes code to a python file called 'name',
        erasing the previous contents."""

        file_path = self.get_path('%s.py'%name)
        with open(file_path,'w') as f:
            f.write(code)

    def clean_code(self, name, forbidden):
        """Remove lines containing items in forbidden from the code.
        Helpful for executing converted notebooks that still retain IPython
        magic commands.
        """

        code = self.read_code(name)
        code = code.split('\n')
        new_code = []
        for i,line in enumerate(code):
            if not [bad for bad in forbidden if bad in line]:
                new_code.append(line)
        new_code = '\n'.join(new_code)
        self.write_code(name, new_code)

    def do_notebook(self, name):
        """Runs a notebook file after optionally
        converting it to a python file."""

        CONVERT_NOTEBOOKS = int(os.getenv('CONVERT_NOTEBOOKS',True))
        s = StringIO()
        if mock:
            with unittest.mock.patch('sys.stdout', new=MockDevice(s)) as fake_out:
                with unittest.mock.patch('sys.stderr', new=MockDevice(s)) as fake_out:
                    self._do_notebook(name, CONVERT_NOTEBOOKS)
        else:
            self._do_notebook(name, CONVERT_NOTEBOOKS)
        self.assertTrue(True)

    def _do_notebook(self, name, convert_notebooks=False):
        s = StringIO()
        if convert_notebooks:
            self.convert_and_execute_notebook(name)
        else:
            self.execute_notebook(name)


class MockDevice(TextIOWrapper):
    """A mock device to temporarily suppress output to stdout
    Similar to UNIX /dev/null.
    """

    def write(self, s):
        if s.startswith('[') and s.endswith(']'):
            super(MockDevice,self).write(s)


def import_all_modules(package):
    """Recursively imports all subpackages, modules, and submodules of a
    given package.
    'package' should be an imported package, not a string.
    """

    for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__,
                                                          onerror=lambda x: None):
        print(modname,ispkg)
        if ispkg:
            subpackage = importlib.import_module('%s.%s' % \
                                                 (package.__name__,modname))
            import_all_modules(subpackage)


def import_module_from_path(module_path, name=None):
    directory,file_name = os.path.split(module_path)
    if name is None:
        name = file_name.rstrip('.py')
        if name == '__init__':
            name = os.path.split(directory)[1]
    try:
        from importlib.machinery import SourceFileLoader
        sfl = SourceFileLoader(name, module_path)
        module = sfl.load_module()
    except ImportError:
        sys.path.append(directory)
        from importlib import import_module
        module_name = file_name.rstrip('.py')
        module = import_module(module_name)
        sys.path.pop() # Remove the directory that was just added.  
    return module


def dict_hash(d):
    pickled = pickle.dumps([(key,d[key]) for key in sorted(d)])
    return hashlib.sha224(pickled).hexdigest()


def method_cache(by='value',method='run'):
    """A decorator used on any model method which calls the model's 'method' 
    method if that latter method has not been called using the current 
    arguments or simply sets model attributes to match the run results if 
    it has."""  
    
    def decorate_(func):
        def decorate(*args, **kwargs):
            model = args[0] # Assumed to be self.  
            assert hasattr(model,method), "Model must have a '%s' method."%method
            if func.__name__ == method: # Run itself.  
                method_args = kwargs
            else: # Any other method.  
                method_args = kwargs[method] if method in kwargs else {}
            if not hasattr(model.__class__,'cached_runs'): # If there is no run cache.  
                model.__class__.cached_runs = {} # Create the method cache.  
            cache = model.__class__.cached_runs
            if by == 'value':
                model_dict = {key:value for key,value in list(model.__dict__.items()) \
                              if key[0]!='_'}
                method_signature = dict_hash({'attrs':model_dict,'args':method_args}) # Hash key.
            elif by == 'instance':
                method_signature = dict_hash({'id':id(model),'args':method_args}) # Hash key.
            else:
                raise ValueError("Cache type must be 'value' or 'instance'")
            if method_signature not in cache:
                print("Method with this signature not found in the cache. Running...")
                f = getattr(model,method)
                f(**method_args)
                cache[method_signature] = (datetime.now(),model.__dict__.copy())
            else:
                print("Method with this signature found in the cache. Restoring...")
                timestamp,attrs = cache[method_signature]
                model.__dict__.update(attrs)
            return func(*args, **kwargs)
        return decorate
    return decorate_


class_intern = cypy.intern

method_memoize = cypy.memoize


class Versioned(object):
    """
    A Mixin class for SciUnit model instances, which provides a version string
    based on the Git repository where the model is tracked.
    Provided by Andrew Davison in issue #53.
    """

    def get_repo(self):
        module = sys.modules[self.__module__]
        # We use module.__file__ instead of module.__path__[0]
        # to include modules without a __path__ attribute.
        path = os.path.realpath(module.__file__)
        repo = git.Repo(path, search_parent_directories=True)
        return repo
    
    def get_version(self):
        repo = self.get_repo()
        head = repo.head
        version = head.commit.hexsha
        if repo.is_dirty():
            version += "*"
        return version
    version = property(get_version)
    
    def get_remote_url(self, remote='origin'):
        repo = self.get_repo()
        remotes = {r.name:r for r in repo.remotes}
        r = repo.remotes[0] if remote not in remotes else remotes[remote]
        try:
            url = list(r.urls)[0]
        except GitCommandError as ex:
            if 'correct access rights' in str(ex):
                # If ssh is not setup to access this repository                                                                                            
                url = Git().execute(['git','config','--get','remote.%s.url' % r.name])
            else:
                raise ex
        return url
    remote_url = property(get_remote_url)
