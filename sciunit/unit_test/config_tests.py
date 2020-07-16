"""Unit tests for user configuration"""

import unittest, json
import sciunit


class ConfigTestCase(unittest.TestCase):
    """Unit tests for config files"""

    def test_json_config(self):
        from sciunit.utils import config_get, create_config

        from pathlib import Path
        config_path = Path.home() / ".sciunit" / "config.json"
        json_content = {"cmap_high": 218, "cmap_low": 38}
        create_config(json_content)
            
        self.assertTrue(config_path.is_file())
        print(config_path)
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
