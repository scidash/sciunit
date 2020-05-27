import unittest
import sciunit

class BaseCase(unittest.TestCase):
    """Unit tests for config files"""
    def test_deep_exclude(self):
        from sciunit.base import deep_exclude
        test_state = {'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5}
        test_exclude = [('a', 'b'), ('c', 'd')]
        deep_exclude(test_state, test_exclude)
    def test_default(self):
        # TODO
        pass

    def test_SciUnit(self):
        from sciunit.base import SciUnit
        sciunitObj = SciUnit()
        self.assertIsInstance(sciunitObj.properties, dict)
        self.assertIsInstance(sciunitObj.dict_hash({'1':1, '2':2}), str)
        self.assertIsInstance(sciunitObj._id, int)
        sciunitObj.json(string=False)
        self.assertIsInstance(sciunitObj._class, dict)

    def test_Versioned(self):
        # TODO
        pass