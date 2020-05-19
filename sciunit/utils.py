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
import contextlib
import traceback
from io import TextIOWrapper, StringIO
from datetime import datetime
try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

import bs4
import nbformat
import nbconvert
from nbconvert.preprocessors import ExecutePreprocessor
try:
    from nbconvert.preprocessors.execute import CellExecutionError
except:
    from nbconvert.preprocessors import CellExecutionError
from quantities.dimensionality import Dimensionality
from quantities.quantity import Quantity
import cypy
from IPython.display import HTML, display

import sciunit
from sciunit.errors import Error
from .base import SciUnit, FileNotFoundError, tkinter
from .base import PLATFORM, PYTHON_MAJOR_VERSION
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, TextIO

try:
    import unittest.mock
    mock = True
except ImportError:
    mock = False
mock = False  # mock is probably obviated by the unittest -b flag.

settings = {'PRINT_DEBUG_STATE': False,  # printd does nothing by default.
            'LOGGING': True,
            'PREVALIDATE': False,
            'KERNEL': ('ipykernel' in sys.modules),
            'CWD': os.path.realpath(sciunit.__path__[0])}


def warn_with_traceback(message: str, category, filename: str, lineno: int,
                        file: TextIO=None, line: str=None) -> None:
    """A function to use with `warnings.showwarning` to show a traceback.

    Args:
        message (str): [description]
        category ([type]): [description]
        filename (str): [description]
        lineno (int): [description]
        file (TextIO, optional): [description]. Defaults to None.
        line (str, optional): [description]. Defaults to None.
    """
    log = file if hasattr(file, 'write') else sys.stderr
    traceback.print_stack(file=log)
    log.write(warnings.formatwarning(
                message, category, filename, lineno, line))


def set_warnings_traceback(tb: bool=True) -> None:
    """Set to `True` to give tracebacks for all warnings, or `False` to restore
    default behavior.

    Args:
        tb (bool, optional): Defaults to True.
    """
    if tb:
        warnings._showwarning = warnings.showwarning
        warnings.showwarning = warn_with_traceback
        warnings.simplefilter("always")
    else:
        warnings.showwarning = warnings._showwarning
        warnings.simplefilter("default")


def dict_combine(*dict_list) -> Dict[Any, Any]:
    """Return the union of several dictionaries.
    Uses the values from later dictionaries in the argument list when
    duplicate keys are encountered.
    In Python 3 this can simply be {**d1, **d2, ...}
    but Python 2 does not support this dict unpacking syntax.

    Returns:
        Dict[Any, Any]: the dict from combining the dicts
    """
    return {k: v for d in dict_list for k, v in d.items()}


def rec_apply(func: Callable, n: int) -> Callable:
    """Used to determine parent directory n levels up
    by repeatedly applying os.path.dirname

    Args:
        func (Callable): [description]
        n (int): [description]

    Returns:
        Callable: [description]
    """
    if n > 1:
        rec_func = rec_apply(func, n - 1)
        return lambda x: func(rec_func(x))
    return func


def printd_set(state: bool) -> None:
    """Enable the printd function.
    Call with True for all subsequent printd commands to be passed to print.
    Call with False to ignore all subsequent printd commands.

    Args:
        state (bool): [description]
    """

    global settings
    settings['PRINT_DEBUG_STATE'] = (state is True)


def printd(*args, **kwargs) -> bool:
    """Print if PRINT_DEBUG_STATE is True

    Returns:
        bool: [description]
    """

    global settings
    if settings['PRINT_DEBUG_STATE']:
        print(*args, **kwargs)
        return True
    return False


if PYTHON_MAJOR_VERSION == 3:
    redirect_stdout = contextlib.redirect_stdout
else:  # Python 2
    @contextlib.contextmanager
    def redirect_stdout(target):
        original = sys.stdout
        sys.stdout = target
        yield
        sys.stdout = original


def assert_dimensionless(value: Union[float, Quantity]) -> float:
    """Tests for dimensionlessness of input.
    If input is dimensionless but expressed as a Quantity, it returns the
    bare value. If it not, it raised an error.
    

    Args:
        value (Union[float, Quantity]): [description]

    Raises:
        TypeError: "Score value must be dimensionless"

    Returns:
        float: [description]
    """

    if isinstance(value, Quantity):
        value = value.simplified
        if value.dimensionality == Dimensionality({}):
            value = value.base.item()
        else:
            raise TypeError("Score value %s must be dimensionless" % value)
    return value


class NotebookTools(object):
    """A class for manipulating and executing Jupyter notebooks.

    Attributes:
        path (str): Relative path to the parent directory of the notebook.
        gen_dir_name (str): Name of directory where files generated by do_notebook are stored
        gen_file_level (int): Number of levels up from notebook directory where generated files are stored.
    """

    # Relative path to the parent directory of the notebook.
    path = ''

    # Name of directory where files generated by do_notebook are stored
    gen_dir_name = 'GeneratedFiles'

    # Number of levels up from notebook directory
    # where generated files are stored
    gen_file_level = 2

    def __init__(self, *args, **kwargs):
        super(NotebookTools, self).__init__(*args, **kwargs)
        self.fix_display()

    @classmethod
    def convert_path(cls, file: Union[str, list]) -> Union[str, int]:
        """Check to see if an extended path is given and convert appropriately

        Args:
            file (Union[str, list]): [description]

        Returns:
            Union[str, int]: [description]
        """

        if isinstance(file, str):
            return file
        elif isinstance(file, list) and \
                all([isinstance(x, str) for x in file]):
            return "/".join(file)
        else:
            print("Incorrect path specified")
            return -1

    def get_path(self, file: str) -> str:
        """Get the full path of the notebook found in the directory
        specified by self.path.
        

        Args:
            file (str): [description]

        Returns:
            str: [description]
        """

        class_path = inspect.getfile(self.__class__)
        parent_path = os.path.dirname(class_path)
        path = os.path.join(parent_path, self.path, file)
        return os.path.realpath(path)

    def fix_display(self) -> None:
        """If this is being run on a headless system the Matplotlib
        backend must be changed to one that doesn't need a display.
        """

        try:
            tkinter.Tk()
        except (tkinter.TclError, NameError):  # If there is no display.
            try:
                import matplotlib as mpl
            except ImportError:
                pass
            else:
                printd("Setting matplotlib backend to Agg")
                mpl.use('Agg')

    def load_notebook(self, name: str) -> Tuple[nbformat.NotebookNode, TextIO]:
        """Loads a notebook file into memory.

        Args:
            name (str): name of the notebook file

        Returns:
            Tuple[nbformat.NotebookNode, TextIO]: The notebook that was read and the file object of the notebook file
        """

        with open(self.get_path('%s.ipynb' % name)) as f:
            nb = nbformat.read(f, as_version=4)
        return nb, f

    def run_notebook(self, nb: nbformat.NotebookNode, f: TextIO) -> None:
        """Runs a loaded notebook file.

        Args:
            nb (nbformat.NotebookNode): The notebook that was loaded.
            f (TextIO): the file object of the notebook file

        Raises:
            Exception: The exception that is thrown when running the notebook
        """

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

    def execute_notebook(self, name: str) -> None:
        """Loads and then runs a notebook file.

        Args:
            name (str): name of the notebook file
        """

        warnings.filterwarnings("ignore", category=DeprecationWarning)
        nb, f = self.load_notebook(name)
        self.run_notebook(nb, f)
        self.assertTrue(True)

    def convert_notebook(self, name: str) -> None:
        """Converts a notebook into a python file.

        Args:
            name (str): name of the notebook file
        """
        exporter = nbconvert.exporters.python.PythonExporter()
        relative_path = self.convert_path(name)
        file_path = self.get_path("%s.ipynb" % relative_path)
        code = exporter.from_filename(file_path)[0]
        self.write_code(name, code)
        self.clean_code(name, [])

    def convert_and_execute_notebook(self, name: str) -> None:
        """Converts a notebook into a python file and then runs it.

        Args:
            name (str): name of the notebook file
        """
        self.convert_notebook(name)
        code = self.read_code(name)
        exec(code, globals())

    def gen_file_path(self, name: str) -> str:
        """Returns full path to generated files.  
        
        Checks to see if directory exists where generated files 
        are stored and creates one otherwise.
        
        Args:
            name (str): [description]

        Returns:
            str: [description]
        """
        relative_path = self.convert_path(name)
        file_path = self.get_path("%s.ipynb" % relative_path)
        parent_path = rec_apply(os.path.dirname,
                                self.gen_file_level)(file_path)
        # Name of generated file
        gen_file_name = name if isinstance(name, str) else name[1]
        gen_dir_path = self.get_path(os.path.join(parent_path,
                                                  self.gen_dir_name))
        # Create folder for generated files if needed
        if not os.path.exists(gen_dir_path):
            os.makedirs(gen_dir_path)
        new_file_path = self.get_path('%s.py' % os.path.join(gen_dir_path,
                                                             gen_file_name))
        return new_file_path

    def read_code(self, name: str) -> str:
        """Reads code from a python file called 'name'

        Args:
            name (str): name of the python file

        Returns:
            str: the code in the python file
        """

        file_path = self.gen_file_path(name)
        with open(file_path) as f:
            code = f.read()
        return code

    def write_code(self, name: str, code: str) -> None:
        """Writes code to a python file called 'name', erasing the previous contents.

        Files are created in a directory specified by gen_dir_name
        (see function gen_file_path)
        File name is second argument of path

        Args:
            name (str): name of the file
            code (str): code to be added into the file
        """

        
        file_path = self.gen_file_path(name)
        with open(file_path, 'w') as f:
            f.write(code)

    def clean_code(self, name: str, forbidden: List[Any]) -> str:
        """Remove lines containing items in 'forbidden' from the code.
        Helpful for executing converted notebooks that still retain IPython
        magic commands.

        Args:
            name (str): name of the notebook file
            forbidden (List[Any]): [description]

        Returns:
            str: [description]
        """

        code = self.read_code(name)
        code = code.split('\n')
        new_code = []
        for line in code:
            if [bad for bad in forbidden if bad in line]:
                pass
            else:
                # Magics where we want to keep the command
                allowed = ['time', 'timeit']
                line = self.strip_line_magic(line, allowed)
                if isinstance(line, list):
                    line = ' '.join(line)
                new_code.append(line)
        new_code = '\n'.join(new_code)
        self.write_code(name, new_code)
        return new_code

    @classmethod
    def strip_line_magic(cls, line: str, magics_allowed: List[str]) -> str:
        """Handles lines that contain get_ipython.run_line_magic() commands

        Args:
            line (str): the line that contain get_ipython.run_line_magic() commands
            magics_allowed (List[str]): [description]

        Returns:
            str: line after being stripped
        """
        if PYTHON_MAJOR_VERSION == 2:  # Python 2
            stripped, magic_kind = cls.strip_line_magic_v2(line)
        else:  # Python 3+
            stripped, magic_kind = cls.strip_line_magic_v3(line)
        if line == stripped:
            printd("No line magic pattern match in '%s'" % line)
        if magic_kind and magic_kind not in magics_allowed:
            # If the part after the magic won't work, just get rid of it
            stripped = ""
        return stripped

    @classmethod
    def strip_line_magic_v3(cls, line: str) -> Tuple[str, str]:
        """strip_line_magic() implementation for Python 3

        Args:
            line (str): [description]

        Returns:
            Tuple[str, str]: [description]
        """

        matches = re.findall("run_line_magic\(([^]]+)", line)
        if matches and matches[0]:  # This line contains the pattern
            match = matches[0]
            if match[-1] == ')':
                match = match[:-1]  # Just because the re way is hard
            magic_kind, stripped = eval(match)
        else:
            stripped = line
            magic_kind = ""
        return stripped, magic_kind

    @classmethod
    def strip_line_magic_v2(cls, line: str) -> Tuple[str, str]:
        """strip_line_magic() implementation for Python 2"""

        matches = re.findall("magic\(([^]]+)", line)
        if matches and matches[0]:  # This line contains the pattern
            match = matches[0]
            if match[-1] == ')':
                match = match[:-1]  # Just because the re way is hard
            stripped = eval(match)
            magic_kind = stripped.split(' ')[0]
            if len(stripped.split(' ')) > 1:
                stripped = stripped.split(' ')[1:]
            else:
                stripped = ""
        else:
            stripped = line
            magic_kind = ""
        return stripped, magic_kind

    def do_notebook(self, name: str) -> None:
        """Run a notebook file after optionally
        converting it to a python file.

        Args:
            name (str): name of the notebook file
        """
        CONVERT_NOTEBOOKS = int(os.getenv('CONVERT_NOTEBOOKS', True))
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

    def _do_notebook(self, name: str, convert_notebooks: bool=False) -> None:
        """ Called by do_notebook to actually run the notebook.

        Args:
            name (str): name of the notebook file
            convert_notebooks (bool): True if the notebook need conversion before executing. Defaults to False.
        """
        if convert_notebooks:
            self.convert_and_execute_notebook(name)
        else:
            self.execute_notebook(name)


class MockDevice(TextIOWrapper):
    """A mock device to temporarily suppress output to stdout
    Similar to UNIX /dev/null.
    """

    def write(self, s) -> None:
        """[summary]

        Args:
            s ([type]): [description]
        """
        if s.startswith('[') and s.endswith(']'):
            super(MockDevice, self).write(s)


def import_all_modules(package, skip: list=None, verbose: bool=False, prefix: str="", depth: int=0) -> None:
    """Recursively imports all subpackages, modules, and submodules of a
    given package.
    'package' should be an imported package, not a string.
    'skip' is a list of modules or subpackages not to import.
    Args:
        package ([type]): [description]
        skip (list, optional): [description]. Defaults to None.
        verbose (bool, optional): [description]. Defaults to False.
        prefix (str, optional): [description]. Defaults to "".
        depth (int, optional): [description]. Defaults to 0.
    """


    skip = [] if skip is None else skip

    for ff, modname, ispkg in pkgutil.walk_packages(path=package.__path__,
                                                    prefix=prefix,
                                                    onerror=lambda x: None):
        if ff.path not in package.__path__[0]:  # Solves weird bug
            continue
        if verbose:
            print('\t'*depth, modname)
        if modname in skip:
            if verbose:
                print('\t'*depth, '*Skipping*')
            continue
        module = '%s.%s' % (package.__name__, modname)
        subpackage = importlib.import_module(module)
        if ispkg:
            import_all_modules(subpackage, skip=skip,
                               verbose=verbose, depth=depth+1)


def import_module_from_path(module_path: str, name=None) -> "ModuleType":
    """[summary]

    Args:
        module_path (str): [description]
        name (str): [description]. Defaults to None.

    Returns:
        ModuleType: [description]
    """
    directory, file_name = os.path.split(module_path)
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
        sys.path.pop()  # Remove the directory that was just added.
    return module


def dict_hash(d):
    return SciUnit.dict_hash(d)


def method_cache(by: str='value', method: str='run') -> Callable:
    """A decorator used on any model method which calls the model's 'method'
    method if that latter method has not been called using the current
    arguments or simply sets model attributes to match the run results if
    it has.

    Args:
        by (str, optional): [description]. Defaults to 'value'.
        method (str, optional): the method that being called. Defaults to 'run'.

    Returns:
        Callable: [description]
    """

    def decorate_(func):
        def decorate(*args, **kwargs):
            model = args[0]  # Assumed to be self.
            assert hasattr(model, method), \
                "Model must have a '%s' method." % method
            if func.__name__ == method:  # Run itself.
                method_args = kwargs
            else:  # Any other method.
                method_args = kwargs[method] if method in kwargs else {}
            # If there is no run cache.
            if not hasattr(model.__class__, 'cached_runs'):
                # Create the method cache.
                model.__class__.cached_runs = {}
            cache = model.__class__.cached_runs
            if by == 'value':
                model_dict = {key: value for key, value in
                              list(model.__dict__.items()) if key[0] != '_'}
                method_signature = SciUnit.dict_hash(
                    {'attrs': model_dict, 'args': method_args})  # Hash key.
            elif by == 'instance':
                method_signature = SciUnit.dict_hash(
                    {'id': id(model), 'args': method_args})  # Hash key.
            else:
                raise ValueError("Cache type must be 'value' or 'instance'")
            if method_signature not in cache:
                print(("Method with this signature not found in the cache. "
                       "Running..."))
                f = getattr(model, method)
                f(**method_args)
                cache[method_signature] = (datetime.now(),
                                           model.__dict__.copy())
            else:
                print(("Method with this signature found in the cache. "
                       "Restoring..."))
                _, attrs = cache[method_signature]
                model.__dict__.update(attrs)
            return func(*args, **kwargs)
        return decorate
    return decorate_


class_intern = cypy.intern

method_memoize = cypy.memoize


def log(*args, **kwargs) -> None:
    """[summary]
    """
    if settings['LOGGING']:
        if settings['KERNEL']:
            kernel_log(*args, **kwargs)
        else:
            non_kernel_log(*args, **kwargs)


def non_kernel_log(*args, **kwargs) -> None:
    """[summary]
    """
    args = [bs4.BeautifulSoup(x, "lxml").text
            if not isinstance(x, Exception) else x
            for x in args]
    try:
        print(*args, **kwargs)
    except SyntaxError:  # Python 2
        print(args)


def kernel_log(*args, **kwargs) -> None:
    """[summary]
    """
    with StringIO() as f:
        kwargs['file'] = f
        args = [u'%s' % arg for arg in args]
        try:
            print(*args, **kwargs)
        except SyntaxError:  # Python 2
            print(args)
        output = f.getvalue()
    display(HTML(output))


def config_get_from_path(config_path: str, key: str) -> int:
    """[summary]

    Args:
        config_path (str): [description]
        key (str): [description]

    Raises:
        Error: [description]
        Error: [description]
        Error: [description]

    Returns:
        int: [description]
    """
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


def config_get(key: str, default: Optional[int]=None) -> int:
    """[summary]

    Args:
        key (str): [description]
        default (Optional[int], optional): [description]. Defaults to None.

    Raises:
        e: [description]

    Returns:
        int: [description]
    """
    try:
        assert isinstance(key, str), "Config key must be a string"
        config_path = os.path.join(settings['CWD'], 'config.json')
        value = config_get_from_path(config_path, key)
    except Exception as e:
        if default is not None:
            log(e)
            log("Using default value of %s" % default)
            value = default
        else:
            raise e
    return value


def path_escape(path: str):
    """Escape a path by placing backslashes in front of disallowed characters

    Args:
        path (str): original path

    Returns:
        str: the new path with the backslashes
    """
    for char in [' ', '(', ')']:
        path = path.replace(char, '\%s' % char)
    return path
