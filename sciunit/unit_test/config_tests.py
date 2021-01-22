"""Unit tests for user configuration"""

import unittest

import sciunit


class ConfigTestCase(unittest.TestCase):
    """Unit tests for config files"""

    def test_json_config(self):
        from pathlib import Path

        from sciunit.utils import DEFAULT_CONFIG, config_get, create_config

        config_path = Path.home() / ".sciunit" / "config.json"
        create_config(DEFAULT_CONFIG)

        self.assertTrue(config_path.is_file())
        cmap_low = config_get("cmap_low")

        self.assertTrue(isinstance(cmap_low, int))
        dummy = config_get("dummy", 37)
        self.assertEqual(dummy, 37)
        try:
            config_get("dummy")
        except sciunit.Error as e:
            self.assertTrue("does not contain key" in str(e))


if __name__ == "__main__":
    unittest.main()
