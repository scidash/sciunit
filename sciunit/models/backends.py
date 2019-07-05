"""Base class for simulator backends for SciUnit models."""

import os
import inspect
import tempfile
import pickle
import shelve

available_backends = {}


def register_backends(vars):
    """Register backends for use with models.

    `vars` should be a dictionary of variables obtained from e.g. `locals()`,
    at least some of which are Backend classes, e.g. from imports.
    """
    new_backends = {x.replace('Backend', ''): cls
                    for x, cls in vars.items()
                    if inspect.isclass(cls) and issubclass(cls, Backend)}
    available_backends.update(new_backends)


class Backend(object):
    """Base class for simulator backends.

    Should only be used with model classes derived from `RunnableModel`.
    Supports caching of simulation results.
    Backend classes should implement simulator-specific
    details of modifying, running, and reading results from the simulation.
    """

    def init_backend(self, *args, **kwargs):
        """Initialize the backend."""
        self.model.attrs = {}

        self.use_memory_cache = kwargs.get('use_memory_cache', True)
        if self.use_memory_cache:
            self.init_memory_cache()
        self.use_disk_cache = kwargs.get('use_disk_cache', False)
        if self.use_disk_cache:
            self.init_disk_cache()
        self.load_model()
        self.model.unpicklable += ['_backend']

    """Name of the backend"""
    name = None

    """The function that handles running the simulation"""
    f = None

    """Optional list of state variables for a backend to record."""
    recorded_variables = None

    def init_cache(self):
        """Initialize the cache."""
        self.init_memory_cache()
        self.init_disk_cache()

    def init_memory_cache(self):
        """Initialize the in-memory version of the cache."""
        self.memory_cache = {}

    def init_disk_cache(self):
        """Initialize the on-disk version of the cache."""
        try:
            # Cleanup old disk cache files
            path = self.disk_cache_location
            os.remove(path)
        except Exception:
            pass
        self.disk_cache_location = os.path.join(tempfile.mkdtemp(), 'cache')

    def get_memory_cache(self, key=None):
        """Return result in memory cache for key 'key' or None if not found."""
        key = self.model.hash if key is None else key
        self._results = self.memory_cache.get(key)
        return self._results

    def get_disk_cache(self, key=None):
        """Return result in disk cache for key 'key' or None if not found."""
        key = self.model.hash if key is None else key
        if not getattr(self, 'disk_cache_location', False):
            self.init_disk_cache()
        disk_cache = shelve.open(self.disk_cache_location)
        self._results = disk_cache.get(key)
        disk_cache.close()
        return self._results

    def set_memory_cache(self, results, key=None):
        """Store result in memory cache with key matching model state."""
        key = self.model.hash if key is None else key
        self.memory_cache[key] = results

    def set_disk_cache(self, results, key=None):
        """Store result in disk cache with key matching model state."""
        if not getattr(self, 'disk_cache_location', False):
            self.init_disk_cache()
        disk_cache = shelve.open(self.disk_cache_location)
        key = self.model.hash if key is None else key
        disk_cache[key] = results
        disk_cache.close()

    def load_model(self):
        """Load the model into memory."""
        pass

    def set_attrs(self, **attrs):
        """Set model attributes on the backend."""
        pass

    def set_run_params(self, **run_params):
        """Set model attributes on the backend."""
        pass

    def backend_run(self):
        """Check for cached results; then run the model if needed."""
        key = self.model.hash
        if self.use_memory_cache and self.get_memory_cache(key):
            return self._results
        if self.use_disk_cache and self.get_disk_cache(key):
            return self._results
        results = self._backend_run()
        if self.use_memory_cache:
            self.set_memory_cache(results, key)
        if self.use_disk_cache:
            self.set_disk_cache(results, key)
        return results

    def _backend_run(self):
        """Run the model via the backend."""
        raise NotImplementedError("Each backend must implement '_backend_run'")

    def save_results(self, path='.'):
        """Save results on disk."""
        with open(path, 'wb') as f:
            pickle.dump(self.results, f)


class BackendException(Exception):
    """Generic backend exception class."""
    pass
