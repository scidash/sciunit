"""Setup file for SciUnit"""

import sys
import os
from pathlib import Path

try:
    from pip.req import parse_requirements
    from pip.download import PipSession
except ImportError:
    from pip._internal.req import parse_requirements
    try:
        from pip._internal.download import PipSession
    except ImportError:
        from pip._internal.network.session import PipSession

from setuptools import setup, find_packages

# IPython 6.0+ does not support Python 2.6, 2.7, 3.0, 3.1, or 3.2
if sys.version_info < (3, 3):
    ipython = "ipython>=5.1,<6.0"
else:
    ipython = "ipython>=5.1"

def read_requirements():
    '''parses requirements from requirements.txt'''
    reqs_path = Path(__file__).parent / 'requirements.txt'
    install_reqs = parse_requirements(str(reqs_path), session=PipSession())
    reqs = [str(ir.req) for ir in install_reqs]
    return reqs

def get_version():
    version = {}
    with open(Path(__file__).parent / 'sciunit' / 'version.py') as f:
        exec(f.read(), version)
    return version['__version__']

readme_path = Path(__file__).parent / 'README.md'
with open(readme_path, encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sciunit',
    version=get_version(),
    author='Rick Gerkin',
    author_email='rgerkin@asu.edu',
    packages=find_packages(),
    url='http://sciunit.scidash.org',
    license='MIT',
    description='A test-driven framework for formally validating scientific models against data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    test_suite="sciunit.unit_test.core_tests",
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'sciunit = sciunit.__main__:main'
            ]
        }
    )
