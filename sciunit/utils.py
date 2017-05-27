"""
Utility functions for SciUnit.
"""

from __future__ import print_function
import os
import sys
import subprocess
import warnings

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


class NotebookTools:
    
    path = ''

    def load_notebook(self, name):
        with open(os.path.join(self.path,'%s.ipynb'%name)) as f:
            nb = nbformat.read(f, as_version=4)
        return nb

    def run_notebook(self, nb):
        if (sys.version_info >= (3, 0)):
            kernel_name = 'python3'
        else:
            kernel_name = 'python2'
        ep = ExecutePreprocessor(timeout=600, kernel_name=kernel_name)
        ep.preprocess(nb, {'metadata': {'path': '.'}})
        
    def execute_notebook(self, name):
        warnings.filterwarnings("ignore", category=DeprecationWarning) 
        nb = self.load_notebook(name)
        self.run_notebook(nb)
        self.assertTrue(True)

    def convert_notebook(self, name):
        subprocess.run(["jupyter","nbconvert","--to","python",
                        os.path.join(self.path,'%s.ipynb'%name)])

    def convert_and_execute_notebook(self, name):
        self.convert_notebook(name)
        with open(os.path.join(self.path,'%s.py'%name)) as f:
            code = f.read()
        exec(code,globals())
        self.assertTrue(True)

    def do_notebook(self, name):
        CONVERT_NOTEBOOKS = int(os.getenv('CONVERT_NOTEBOOKS',True))
        if CONVERT_NOTEBOOKS:
            self.convert_and_execute_notebook(name)
        else:
            self.execute_notebook(name)
