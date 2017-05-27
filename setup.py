try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='sciunit',
    version='0.1.5.7',
    author='Rick Gerkin',
    author_email='rgerkin@asu.edu',
    packages=['sciunit', 
              'sciunit.tests'],
    url='http://sciunit.scidash.org',
    license='MIT',
    description='A test-driven framework for formally validating scientific models against data.',
    long_description="",
    install_requires=['cypy>=0.2',
                      'quantities',
                      'pandas>=0.18',
                      'ipython>=5.1',
                      'bs4',
                      'lxml',
                      'nbconvert',
                      'ipykernel',
                      'nbformat',],
    dependency_links = [],
    entry_points={
        'console_scripts': [
            'sciunit = sciunit.__main__:main'
            ]
        }
    )
