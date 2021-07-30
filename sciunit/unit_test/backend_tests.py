"""Unit tests for backends."""

import unittest
from pathlib import Path

from sciunit import Model
from sciunit.models.backends import Backend
from sciunit.utils import NotebookTools

class BackendsTestCase(unittest.TestCase, NotebookTools):
    """Unit tests for the sciunit module"""

    path = "."

    def test_backends(self):
        """Test backends."""
        self.do_notebook("backend_tests")

    def test_backends_init_caches(self):
        myModel = Model()
        backend = Backend()
        backend.model = myModel

        backend.init_backend(use_disk_cache=True, use_memory_cache=True)
        backend.init_backend(use_disk_cache=False, use_memory_cache=True)
        backend.init_backend(use_disk_cache=True, use_memory_cache=False)
        backend.init_backend(use_disk_cache=False, use_memory_cache=False)
        backend.init_cache()

    def test_backends_init_disk_caches(self):
        # Automatically set disk_cache location
        myModel = Model()
        backend = Backend()
        backend.model = myModel
        backend.init_backend(use_disk_cache=True, use_memory_cache=False)
        self.assertTrue(backend.disk_cache_location.endswith(".sciunit/cache"))

        # Manually set disk_cache location (a string)
        myModel = Model()
        backend = Backend()
        backend.model = myModel
        backend.init_backend(use_disk_cache="/some/good/path", use_memory_cache=False)
        self.assertEqual(backend.disk_cache_location, "/some/good/path")

        # Manually set disk_cache location (a Path)
        myModel = Model()
        backend = Backend()
        backend.model = myModel
        backend.init_backend(use_disk_cache=Path("/some/good/path"), use_memory_cache=False)
        self.assertEqual(backend.disk_cache_location, "/some/good/path")

    def test_backends_set_caches(self):
        myModel = Model()
        backend = Backend()
        backend.model = myModel
        backend.init_backend(use_disk_cache=True, use_memory_cache=True)
        backend.clear_disk_cache()
        # backend.init_memory_cache()
        self.assertIsNone(backend.get_disk_cache("key1"))
        self.assertIsNone(backend.get_disk_cache("key2"))
        self.assertIsNone(backend.get_memory_cache("key1"))
        self.assertIsNone(backend.get_memory_cache("key2"))
        backend.set_disk_cache("value1", "key1")
        backend.set_memory_cache("value1", "key1")
        self.assertEqual(backend.get_memory_cache("key1"), "value1")
        self.assertEqual(backend.get_disk_cache("key1"), "value1")
        backend.set_disk_cache("value2")
        backend.set_memory_cache("value2")
        self.assertEqual(backend.get_memory_cache(myModel.hash()), "value2")
        self.assertEqual(backend.get_disk_cache(myModel.hash()), "value2")

        backend.load_model()
        backend.set_attrs(test_attribute="test attribute")
        backend.set_run_params(test_param="test parameter")
        backend.init_backend(use_disk_cache=True, use_memory_cache=True)

    def test_backend_run(self):
        backend = Backend()
        self.assertRaises(NotImplementedError, backend._backend_run)

        class MyBackend(Backend):
            model = Model()

            def _backend_run(self) -> str:
                return "test result"

        backend = MyBackend()
        backend.init_backend(use_disk_cache=True, use_memory_cache=True)
        backend.backend_run()
        backend.set_disk_cache("value1", "key1")
        backend.set_memory_cache("value1", "key1")
        backend.backend_run()
        backend.set_disk_cache("value2")
        backend.set_memory_cache("value2")
        backend.backend_run()

        backend = MyBackend()
        backend.init_backend(use_disk_cache=False, use_memory_cache=True)
        backend.backend_run()
        backend.set_disk_cache("value1", "key1")
        backend.set_memory_cache("value1", "key1")
        backend.backend_run()
        backend.set_disk_cache("value2")
        backend.set_memory_cache("value2")
        backend.backend_run()

        backend = MyBackend()
        backend.init_backend(use_disk_cache=True, use_memory_cache=False)
        backend.backend_run()
        backend.set_disk_cache("value1", "key1")
        backend.set_memory_cache("value1", "key1")
        backend.backend_run()
        backend.set_disk_cache("value2")
        backend.set_memory_cache("value2")
        backend.backend_run()

        backend = MyBackend()
        backend.init_backend(use_disk_cache=False, use_memory_cache=False)
        backend.backend_run()
        backend.set_disk_cache("value1", "key1")
        backend.set_memory_cache("value1", "key1")
        backend.backend_run()
        backend.set_disk_cache("value2")
        backend.set_memory_cache("value2")
        backend.backend_run()

    def test_backend_cache_to_results(self):
        myModel = Model()
        class MyBackend(Backend):
            def cache_to_results(self, cache):
                return { "color": "red" }

            def results_to_cache(self, results):
                return { "color": "blue" }

            def _backend_run(self):
                return { "color": "white" }

        backend = MyBackend()
        backend.model = myModel
        backend.init_backend(use_disk_cache=False, use_memory_cache=True)
        # On first run we get the original object
        self.assertEqual(backend.backend_run(), { "color": "white" })
        # And on consequent runs we get the object recovered from the cache
        self.assertEqual(backend.backend_run(), { "color": "red" })
        self.assertEqual(backend.backend_run(), { "color": "red" })

if __name__ == "__main__":
    unittest.main()
