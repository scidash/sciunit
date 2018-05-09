"""Unit tests for user configuration"""

import unittest
import os

import sciunit

class ConfigTestCase(unittest.TestCase):
    """Unit tests for config files"""

    def test_json_config(self):
        from sciunit.utils import config_get
        config_path = os.path.join(sciunit.__path__[0],'config.json')
        print(config_path)
        self.assertTrue(os.path.isfile(config_path))
        cmap_low = config_get('cmap_low')
        self.assertTrue(isinstance(cmap_low,int))
        dummy = config_get('dummy',37)
        self.assertEqual(dummy,37)
        try:
            config_get('dummy')
        except sciunit.Error as e:
            self.assertTrue('does not contain key' in str(e))