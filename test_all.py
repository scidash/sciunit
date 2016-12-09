import unittest
import sys
import warnings

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

class DocumentationTestCase(unittest.TestCase):
    def load_notebook(self,name):
        f = open('docs/%s.ipynb' % name)
        nb = nbformat.read(f, as_version=4)
        return f,nb

    def run_notebook(self,nb):
        if (sys.version_info >= (3, 0)):
            kernel_name = 'python3'
        else:
            kernel_name = 'python2'
        ep = ExecutePreprocessor(timeout=600, kernel_name=kernel_name)
        ep.preprocess(nb, {'metadata': {'path': 'docs/'}})
        
    def execute_notebook(self,name):
        warnings.filterwarnings("ignore", category=DeprecationWarning) 
        f,nb = self.load_notebook(name)
        self.run_notebook(nb)
        f.close()
        self.assertTrue(True)

    def test_chapter1(self):
        print(sys.path)
        sys.path.append(os.getcwd())
        print(sys.path)
        self.execute_notebook('chapter1')
    
    def test_chapter2(self):
        self.execute_notebook('chapter2')
    
    def test_chapter3(self):
        self.execute_notebook('chapter3')

if __name__ == '__main__':
    unittest.main()
        
