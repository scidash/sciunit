import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# IPython 6.0+ does not support Python 2.6, 2.7, 3.0, 3.1, or 3.2
if sys.version_info < (3,3):
    ipython = "ipython>=5.1,<6.0"
else:
    ipython = "ipython>=5.1"    
    
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
    install_requires=['cypy>=0.2',
                      'quantities==0.12.1',
                      #'quantities==999',
                      'pandas>=0.18',
                      ipython,
                      'matplotlib',
                      'bs4',
                      'lxml',
                      'nbconvert',
                      'ipykernel',
                      'nbformat',
                      'gitpython'],
    #dependency_links = ['git+https://github.com/python-quantities/python-quantities.git@master#egg=quantities-999'],
    entry_points={
        'console_scripts': [
            'sciunit = sciunit.__main__:main'
            ]
        }
    )



