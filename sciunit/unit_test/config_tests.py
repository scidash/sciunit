"""Unit tests for user configuration"""

import unittest, json
import sciunit


class ConfigTestCase(unittest.TestCase):
    """Unit tests for config files"""

    def test_json_config(self):
        from sciunit.utils import config_get

        from pathlib import Path
        config_dir = Path.home() / ".sciunit"
        config_dir.mkdir(exist_ok=True, parents=True)
        config_path = config_dir / "config.json"
        json_content = {"cmap_high": 218, "cmap_low": 38}
        with open (config_path, "w") as outfile:
            json.dump(json_content, outfile)
            
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
