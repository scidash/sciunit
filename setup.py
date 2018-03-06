"""Setup file for SciUnit"""

import sys
import os

from pip.req import parse_requirements
from pip.download import PipSession

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# IPython 6.0+ does not support Python 2.6, 2.7, 3.0, 3.1, or 3.2
if sys.version_info < (3,3):
    ipython = "ipython>=5.1,<6.0"
else:
    ipython = "ipython>=5.1"    

def read_requirements():
    '''parses requirements from requirements.txt'''
    reqs_path = os.path.join('.', 'requirements.txt')
    install_reqs = parse_requirements(reqs_path, session=PipSession())
    reqs = [str(ir.req) for ir in install_reqs]
    return reqs
    
setup(
    name='sciunit',
    version='0.19',
    author='Rick Gerkin',
    author_email='rgerkin@asu.edu',
    packages=['sciunit',
              'sciunit.scores',
              'sciunit.unit_test'],
    url='http://sciunit.scidash.org',
    license='MIT',
    description='A test-driven framework for formally validating scientific models against data.',
    long_description="",  
    test_suite="sciunit.unit_test.core_tests",    
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'sciunit = sciunit.__main__:main'
            ]
        }
    )



