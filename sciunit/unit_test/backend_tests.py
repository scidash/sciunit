"""Unit tests for backends."""

from sciunit.models.backends import Backend
from sciunit.utils import NotebookTools
from sciunit import Model
import unittest, pathlib


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

    def test_backends_set_caches(self):
        myModel = Model()
        backend = Backend()
        backend.model = myModel
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
        self.assertEqual(backend.get_memory_cache(myModel.hash), "value2")
        self.assertEqual(backend.get_disk_cache(myModel.hash), "value2")

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



if __name__ == "__main__":
    unittest.main()
