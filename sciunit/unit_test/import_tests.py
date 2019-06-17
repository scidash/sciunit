"""Tests of imports of sciunit submodules and other dependencies"""

import unittest


class ImportTestCase(unittest.TestCase):
    """Unit tests for imports"""

    def test_quantities(self):
        import quantities as pq
        pq.Quantity([10, 20, 30], pq.pA)

    def test_import_everything(self):
        import sciunit
        from sciunit.utils import import_all_modules

        # Recursively import all submodules
        import_all_modules(sciunit)


if __name__ == '__main__':
    unittest.main()
