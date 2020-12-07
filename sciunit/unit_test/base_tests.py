import unittest
import sciunit
import pandas as pd
import numpy as np


class BaseCase(unittest.TestCase):
    """Unit tests for config files"""

    def test_deep_exclude(self):
        from sciunit.base import deep_exclude

        test_state = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
        test_exclude = [("a", "b"), ("c", "d")]
        deep_exclude(test_state, test_exclude)

    def test_default(self):
        # TODO
        pass

    def test_SciUnit(self):
        from sciunit.base import SciUnit

        sciunitObj = SciUnit()
        self.assertIsInstance(sciunitObj.properties, dict)
        self.assertIsInstance(sciunitObj.dict_hash({"1": 1, "2": 2}), str)
        self.assertIsInstance(sciunitObj._id, int)
        self.assertIsInstance(sciunitObj.id, str)
        sciunitObj.json(string=False)
        self.assertIsInstance(sciunitObj._class, dict)
        sciunitObj.testState = "testState"
        print(sciunitObj._state(keys=["testState"]))
        sciunitObj.unpicklable.append("testState")

        self.assertFalse("testState" in sciunitObj.__getstate__())

    def test_Versioned(self):
        from sciunit.base import Versioned
        from git import Remote, Repo

        ver = Versioned()
        self.assertEqual("origin", str(ver.get_remote("I am not a remote")))
        self.assertEqual("origin", str(ver.get_remote()))
        self.assertIsInstance(ver.get_repo(), Repo)
        self.assertIsInstance(ver.get_remote_url("I am not a remote"), str)

    def test_SciUnitEncoder(self):
        from sciunit.base import SciUnitEncoder, SciUnit

        encoderObj = SciUnitEncoder()

        d = {"col1": [1, 2], "col2": [3, 4]}
        df = pd.DataFrame(data=d)
        self.assertIsInstance(encoderObj.default(df), dict)

        npArr = np.ndarray(shape=(2, 2), dtype=int)
        self.assertIsInstance(encoderObj.default(npArr), list)

        sciunitObj = SciUnit()
        sciunitObj.testState = "testState"
        self.assertIsInstance(encoderObj.default(sciunitObj), dict)

        self.assertRaises(TypeError, encoderObj.default, "This is a string")

        class MyClass:
            pass

        self.assertIsInstance(encoderObj.default(MyClass()), str)


if __name__ == "__main__":
    unittest.main()
