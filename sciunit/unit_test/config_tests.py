"""Unit tests for user configuration"""

import unittest
from pathlib import Path

import sciunit


class ConfigTestCase(unittest.TestCase):
    """Unit tests for config files"""

    def test_new_config(self):
        sciunit.config.create()

        self.assertTrue(sciunit.config.path.is_file())
        cmap_low = sciunit.config.get("cmap_low")

        self.assertTrue(isinstance(cmap_low, int))
        dummy = sciunit.config.get("dummy", 37)
        self.assertEqual(dummy, 37)
        try:
            sciunit.config.get("dummy")
        except sciunit.Error as e:
            self.assertTrue("does not contain key" in str(e))

    def test_missing_config(self):
        sciunit.config.path = Path("_delete.json")
        sciunit.config.get_from_disk()

    def test_bad_config(self):
        sciunit.config.path = Path("_delete.json")
        with open(sciunit.config.path, "w") as f:
            f.write(".......")
        sciunit.config.get_from_disk()


if __name__ == "__main__":
    unittest.main()
