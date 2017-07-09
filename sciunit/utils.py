"""
Utility functions for SciUnit.
"""

from __future__ import print_function
import os
import sys
import subprocess
import warnings
try: # Python 3
    import tkinter
except ImportError: # Python 2
    import Tkinter as tkinter
import inspect

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from quantities.dimensionality import Dimensionality
from quantities.quantity import Quantity

PRINT_DEBUG_STATE = False # printd does nothing by default.  


def printd_set(state):
    global PRINT_DEBUG_STATE
    PRINT_DEBUG_STATE = (state is True)


def printd(*args, **kwargs):
    global PRINT_DEBUG_STATE
    if PRINT_DEBUG_STATE:
        print(*args, **kwargs)


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

    def get_path(self):
        class_path = inspect.getfile(self.__class__)
        parent_path = os.path.dirname(class_path)
        return os.path.join(parent_path,self.path)

    def fix_display(self):
        """If this is being run on a headless system the Matplotlib
        backend must be changed to one that doesn't need a display."""
        
        try:
            root = tkinter.Tk()
        except tkinter.TclError: # If there is no display.  
            try:
                import matplotlib as mpl
            except ImportError:
                pass
            else:
                "Setting matplotlib backend to Agg"
                mpl.use('Agg')

    def load_notebook(self, name):
        """Loads a notebook file into memory."""
        
        with open(os.path.join(self.get_path(),'%s.ipynb'%name)) as f:
            nb = nbformat.read(f, as_version=4)
        return nb

    def run_notebook(self, nb):
        """Runs a loaded notebook file."""
        
        if (sys.version_info >= (3, 0)):
            kernel_name = 'python3'
        else:
            kernel_name = 'python2'
        ep = ExecutePreprocessor(timeout=600, kernel_name=kernel_name)
        ep.preprocess(nb, {'metadata': {'path': '.'}})
        
    def execute_notebook(self, name):
        """Loads and then runs a notebook file."""
        
        warnings.filterwarnings("ignore", category=DeprecationWarning) 
        nb = self.load_notebook(name)
        self.run_notebook(nb)
        self.assertTrue(True)

    def convert_notebook(self, name):
        """Converts a notebook into a python file."""
        
        subprocess.run(["jupyter","nbconvert","--to","python",
                        os.path.join(self.get_path(),'%s.ipynb'%name)])
        self.clean_code(name, ['get_ipython'])    

    def convert_and_execute_notebook(self, name):
        """Converts a notebook into a python file and then runs it."""
        
        self.convert_notebook(name)
        code = self.read_code(name)
        exec(code,globals())

    def read_code(self, name):
        """Reads code from a python file called 'name'"""

        with open(os.path.join(self.get_path(),'%s.py'%name)) as f:
            code = f.read()
        return code

    def write_code(self, name, code):
        """Writes code to a python file called 'name', 
        erasing the previous contents."""

        with open(os.path.join(self.get_path(),'%s.py'%name),'r+') as f:
            f.seek(0)
            f.write(code)
            f.truncate()

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
        if CONVERT_NOTEBOOKS:
            self.convert_and_execute_notebook(name)
        else:
            self.execute_notebook(name)
        self.assertTrue(True)
