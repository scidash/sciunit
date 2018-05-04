"""
Utility functions for SciUnit.
"""

from __future__ import print_function
import os
import sys
import warnings
import inspect
import pkgutil
import importlib
import json
import re
from io import TextIOWrapper,StringIO
from datetime import datetime

import bs4
import nbformat
import nbconvert
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors.execute import CellExecutionError
from quantities.dimensionality import Dimensionality
from quantities.quantity import Quantity
import cypy
from IPython.display import HTML,display

import sciunit
from sciunit.errors import Error
from .base import SciUnit,FileNotFoundError,tkinter,PYTHON_MAJOR_VERSION
try:
    import unittest.mock
    mock = True
except ImportError:
    mock = False
mock = False # mock is probably obviated by the unittest -b flag.

settings = {'PRINT_DEBUG_STATE':False, # printd does nothing by default.
            'LOGGING':True,
            'KERNEL':('ipykernel' in sys.modules),
            'CWD':os.path.realpath(sciunit.__path__[0])}

def printd_set(state):
    """Enable the printd function.  
    Call with True for all subsequent printd commands to be passed to print.
    Call with False to ignore all subsequent printd commands.  
    """

    global settings
    settings['PRINT_DEBUG_STATE'] = (state is True)


def printd(*args, **kwargs):
    """Print if PRINT_DEBUG_STATE is True"""

    global settings
    if settings['PRINT_DEBUG_STATE']:
        print(*args, **kwargs)
        return True
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
    """A class for manipulating and executing Jupyter notebooks."""

    def __init__(self, *args, **kwargs):
        super(NotebookTools,self).__init__(*args, **kwargs)
        self.fix_display()

    path = '' # Relative path to the parent directory of the notebook.

    def get_path(self, file):
        """Get the full path of the notebook found in the directory
        specified by self.path.
        """

        class_path = inspect.getfile(self.__class__)
        parent_path = os.path.dirname(class_path)
        path = os.path.join(parent_path,self.path,file)
        return os.path.realpath(path)

    def fix_display(self):
        """If this is being run on a headless system the Matplotlib
        backend must be changed to one that doesn't need a display.
        """

        try:
            tkinter.Tk()
        except (tkinter.TclError, NameError): # If there is no display.
            try:
                import matplotlib as mpl
            except ImportError:
                pass
            else:
                print("Setting matplotlib backend to Agg")
                mpl.use('Agg')

    def load_notebook(self, name):
        """Loads a notebook file into memory."""

        with open(self.get_path('%s.ipynb'%name)) as f:
            nb = nbformat.read(f, as_version=4)
        return nb,f

    def run_notebook(self, nb, f):
        """Runs a loaded notebook file."""
        
        if PYTHON_MAJOR_VERSION == 3:
            kernel_name = 'python3'
        elif PYTHON_MAJOR_VERSION == 2:
            kernel_name = 'python2'
        else:
            raise Exception('Only Python 2 and 3 are supported')
        ep = ExecutePreprocessor(timeout=600, kernel_name=kernel_name)
        try:
            ep.preprocess(nb, {'metadata': {'path': '.'}})
        except CellExecutionError:
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
        self.clean_code(name, [])#'get_ipython'])

    def convert_and_execute_notebook(self, name):
        """Converts a notebook into a python file and then runs it."""

        self.convert_notebook(name)
        code = self.read_code(name)#clean_code(name,'get_ipython')
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
        """Remove lines containing items in 'forbidden' from the code.
        Helpful for executing converted notebooks that still retain IPython
        magic commands.
        """

        code = self.read_code(name)
        code = code.split('\n')
        new_code = []
        for line in code:
            if [bad for bad in forbidden if bad in line]:
                pass
            else:
                allowed = ['time','timeit'] # Magics where we want to keep the command
                line = self.strip_line_magic(line,allowed)
                new_code.append(line)
        new_code = '\n'.join(new_code)
        self.write_code(name, new_code)
        return new_code

    @classmethod
    def strip_line_magic(cls, line, magics_allowed):
        """Handles lines that contain get_ipython.run_line_magic() commands"""
        if PYTHON_MAJOR_VERSION == 2: # Python 2
            stripped,magic_kind = cls.strip_line_magic_v2(line)
        else: # Python 3+
            stripped,magic_kind = cls.strip_line_magic_v3(line)
        if line == stripped:
            printd("No line magic pattern match in '%s'" % line)
        if magic_kind and magic_kind not in magics_allowed:
            stripped = "" # If the part after the magic won't work, 
                          # just get rid of it
        return stripped

    @classmethod
    def strip_line_magic_v3(cls,line):
        """strip_line_magic() implementation for Python 3"""

        matches = re.findall("run_line_magic\(([^]]+)", line)
        if matches and matches[0]: # This line contains the pattern
            match = matches[0]
            if match[-1] == ')':
                match = match[:-1] # Just because the re way is hard
            magic_kind,stripped = eval(match)
        else:
            stripped = line
            magic_kind = ""
        return stripped,magic_kind

    @classmethod
    def strip_line_magic_v2(cls,line):
        """strip_line_magic() implementation for Python 2"""

        matches = re.findall("magic\(([^]]+)", line)
        if matches and matches[0]: # This line contains the pattern
            match = matches[0]
            if match[-1] == ')':
                match = match[:-1] # Just because the re way is hard
            stripped = eval(match)
            magic_kind = stripped.split(' ')[0]
            if len(stripped.split(' '))>1:
                stripped = stripped.split(' ')[1:]
            else:
                stripped = ""
        else:
            stripped = line
            magic_kind = ""
        return stripped,magic_kind

    def do_notebook(self, name):
        """Runs a notebook file after optionally
        converting it to a python file."""

        CONVERT_NOTEBOOKS = int(os.getenv('CONVERT_NOTEBOOKS',True))
        s = StringIO()
        if mock:
            out = unittest.mock.patch('sys.stdout', new=MockDevice(s))
            err = unittest.mock.patch('sys.stderr', new=MockDevice(s))
            self._do_notebook(name, CONVERT_NOTEBOOKS)
            out.close()
            err.close()
        else:
            self._do_notebook(name, CONVERT_NOTEBOOKS)
        self.assertTrue(True)

    def _do_notebook(self, name, convert_notebooks=False):
        """Called by do_notebook to actually run the notebook."""
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


def import_all_modules(package, skip=None, verbose=False, prefix="", depth=0):
    """Recursively imports all subpackages, modules, and submodules of a
    given package.
    'package' should be an imported package, not a string.
    'skip' is a list of modules or subpackages not to import.
    """

    skip = [] if skip is None else skip

    for ff, modname, ispkg in pkgutil.walk_packages(path=package.__path__,
                                                prefix=prefix,
                                                onerror=lambda x: None):
        if ff.path not in package.__path__[0]: # Solves weird bug
            continue
        if verbose:
            print('\t'*depth,modname)
        if modname in skip:
            if verbose:
                print('\t'*depth,'*Skipping*')
            continue
        module = '%s.%s' % (package.__name__,modname)
        subpackage = importlib.import_module(module)
        if ispkg:
            import_all_modules(subpackage, skip=skip, 
                               verbose=verbose,depth=depth+1)


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
    return SciUnit.dict_hash(d)


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
                method_signature = SciUnit.dict_hash({'attrs':model_dict,'args':method_args}) # Hash key.
            elif by == 'instance':
                method_signature = SciUnit.dict_hash({'id':id(model),'args':method_args}) # Hash key.
            else:
                raise ValueError("Cache type must be 'value' or 'instance'")
            if method_signature not in cache:
                print("Method with this signature not found in the cache. Running...")
                f = getattr(model,method)
                f(**method_args)
                cache[method_signature] = (datetime.now(),model.__dict__.copy())
            else:
                print("Method with this signature found in the cache. Restoring...")
                _,attrs = cache[method_signature]
                model.__dict__.update(attrs)
            return func(*args, **kwargs)
        return decorate
    return decorate_


class_intern = cypy.intern

method_memoize = cypy.memoize


def log(*args, **kwargs):
    if settings['LOGGING']:
        if settings['KERNEL']:
            kernel_log(*args, **kwargs)
        else:
            non_kernel_log(*args, **kwargs)


def non_kernel_log(*args, **kwargs):
    args = [bs4.BeautifulSoup(x,"lxml").text \
            if not isinstance(x,Exception) else x \
            for x in args]
    try:
        print(*args, **kwargs)
    except SyntaxError: # Python 2
        print(args)


def kernel_log(*args, **kwargs):
    with StringIO() as f:
        kwargs['file'] = f
        args = [u'%s'%arg for arg in args]
        try:
            print(*args, **kwargs)
        except SyntaxError: # Python 2
            print(args)
        output = f.getvalue()
    display(HTML(output))


def config_get_from_path(config_path,key):
    try:
        with open(config_path) as f:
            config = json.load(f)
            value = config[key]
    except FileNotFoundError:
        raise Error("Config file not found at '%s'" % config_path)
    except json.JSONDecodeError:
        log("Config file JSON at '%s' was invalid" % config_path)
        raise Error("Config file not found at '%s'" % config_path)
    except KeyError:
        raise Error("Config file does not contain key '%s'" % key)
    return value


def config_get(key, default=None):
    try:
        assert isinstance(key,str), "Config key must be a string"
        config_path = os.path.join(settings['CWD'],'config.json')
        value = config_get_from_path(config_path,key)    
    except Exception as e:
        if default is not None:
            log(e)
            log("Using default value of %s" % default)
            value = default
        else:
            raise e
    return value
