"""Setup file for SciUnit"""

from pathlib import Path
from setuptools import setup, find_packages


def read_requirements():
    '''parses requirements from requirements.txt'''
    reqs_path = Path(__file__).parent / 'requirements.txt'
    reqs = None
    with open(reqs_path) as reqs_file:
        reqs = reqs_file.read().splitlines()
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
    description=('A test-driven framework for formally validating scientific '
                 'models against data.'),
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
