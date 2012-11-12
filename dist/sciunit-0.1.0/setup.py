from distutils.core import setup

setup(
	name='sciunit',
	version='0.1.0',
	author='Cyrus Omar',
	author_email='cyrus.omar@gmail.com',
	packages=['sciunit'],
	url='http://pypi.python.org/pypi/sciunit/',
	license='LICENSE',
	description='A test-driven framework for formally validating scientific models against data.',
	long_description=open('README.markdown').read(),
	install_requires=[]
)
