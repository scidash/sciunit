try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
	name='sciunit',
	version='0.1.5.2',
	author='Rick Gerkin',
	author_email='rgerkin@asu.edu',
	packages=['sciunit', 'sciunit.tests'],
	url='http://github.com/scidash/sciunit',
	license='MIT',
	description='A test-driven framework for formally validating scientific models against data.',
	long_description="",
	install_requires=['cypy>=0.2','quantities','pandas','ipython','bs4'],
	dependency_links = ['git+http://github.com/rgerkin/cypy'],
)
