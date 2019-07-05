"""Unit tests for command line tools."""

import unittest
import platform
import os
import tempfile

import sciunit


class CommandLineTestCase(unittest.TestCase):
    """Unit tests for command line tools."""

    def setUp(self):
        from sciunit.__main__ import main

        self.main = main
        path = os.path.abspath(sciunit.__path__[0])
        SCIDASH_HOME = os.path.dirname(os.path.dirname(path))
        self.cosmosuite_path = os.path.join(SCIDASH_HOME, 'scidash')

    def test_sciunit_1create(self):
        try:
            self.main('--directory', self.cosmosuite_path, 'create')
        except Exception as e:
            if 'There is already a configuration file' not in str(e):
                raise e
            else:
                temp_path = tempfile.mkdtemp()
                self.main('--directory', temp_path, 'create')

    def test_sciunit_2check(self):
        self.main('--directory', self.cosmosuite_path, 'check')

    def test_sciunit_3run(self):
        self.main('--directory', self.cosmosuite_path, 'run')

    def test_sciunit_4make_nb(self):
        self.main('--directory', self.cosmosuite_path, 'make-nb')

    # Skip for python versions that don't have importlib.machinery
    @unittest.skipIf(platform.python_version() < '3.3',
                     "run-nb not supported on Python < 3.3")
    def test_sciunit_5run_nb(self):
        self.main('--directory', self.cosmosuite_path, 'run-nb')


if __name__ == '__main__':
    test_program = unittest.main(verbosity=0, buffer=True, exit=False)
