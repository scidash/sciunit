"""Base class for simulator backends for SciUnit models."""

import inspect
import pickle
import shelve
import tempfile
from pathlib import Path
from typing import Any, Union

from sciunit.base import SciUnit, config

available_backends = {}


def register_backends(vars: dict) -> None:
    """Register backends for use with models.

    Args:
        vars (dict): a dictionary of variables obtained from e.g. `locals()`,
                     at least some of which are Backend classes, e.g. from imports.
    """
    new_backends = {
        x if x is None else x.replace("Backend", ""): cls
        for x, cls in vars.items()
        if inspect.isclass(cls) and issubclass(cls, Backend)
    }
    available_backends.update(new_backends)


class Backend(SciUnit):
    """
    Base class for simulator backends.

    Should only be used with model classes derived from `RunnableModel`.
    Supports caching of simulation results.
    Backend classes should implement simulator-specific
    details of modifying, running, and reading results from the simulation.
    """

    def init_backend(self, *args, **kwargs) -> None:
        """Initialize the backend."""
        self.model.attrs = {}

        self.use_memory_cache = kwargs.get("use_memory_cache", True)
        if self.use_memory_cache:
            self.init_memory_cache()
        self.use_disk_cache = kwargs.get("use_disk_cache", False)
        if self.use_disk_cache:
            self.init_disk_cache(location=self.use_disk_cache)
        self.load_model()

    #: Name of the backend
    name = None

    #: The function that handles running the simulation
    f = None

    #: Optional list of state variables for a backend to record.
    recorded_variables = None

    state_hide = ["memory_cache", "_results", "stdout", "exec_in_dir", "model"]

    def init_cache(self) -> None:
        """Initialize the cache."""
        self.init_memory_cache()
        self.init_disk_cache()

    def init_memory_cache(self) -> None:
        """Initialize the in-memory version of the cache."""
        self.memory_cache = {}

    def init_disk_cache(self, location: Union[str, Path, bool, None] = None) -> None:
        """Initialize the on-disk version of the cache."""
        if isinstance(location, (str, Path)):
            location = str(location)
        else:
            # => "~/.sciunit/cache"
            location = str(config.path.parent / "cache")

        self.disk_cache_location = location

    def clear_disk_cache(self) -> None:
        """Removes the cache file from the disk if it exists.
        """
        path = Path(self.disk_cache_location)

        if path.exists():
            with shelve.open(str(path)) as cache:
                cache.clear()

    def get_memory_cache(self, key: str = None) -> dict:
        """Return result in memory cache for key 'key' or None if not found.

        Args:
            key (str, optional): [description]. Defaults to None.

        Returns:
            dict: The memory cache for key 'key' or None if not found.
        """
        key = self.model.hash() if key is None else key
        if not getattr(self, "memory_cache", False):
            self.init_memory_cache()
        self._results = self.memory_cache.get(key)
        return self._results

    def get_disk_cache(self, key: str = None) -> Any:
        """Return result in disk cache for key 'key' or None if not found.

        Args:
            key (str, optional): keys that will be used to find cached data. Defaults to None.

        Returns:
            Any: The disk cache for key 'key' or None if not found.
        """
        key = self.model.hash() if key is None else key
        if not getattr(self, "disk_cache_location", False):
            self.init_disk_cache()
        disk_cache = shelve.open(str(self.disk_cache_location))
        self._results = disk_cache.get(key)
        disk_cache.close()
        return self._results

    def get_cache(self, key: str = None) -> Any:
        """Return result in disk or memory cache for key 'key' or None if not
        found. If both `use_disk_cache` and `use_memory_cache` are True, the
        memory cache is returned.

        Returns:
            Any: The cache for key 'key' or None if not found.
        """
        if self.use_memory_cache:
            result = self.get_memory_cache(key=key)
            if result is not None:
                return result
        if self.use_disk_cache:
            result = self.get_disk_cache(key=key)
            if result is not None:
                return result
        return None

    def set_memory_cache(self, results: Any, key: str = None) -> None:
        """Store result in memory cache with key matching model state.

        Args:
            results (Any): [description]
            key (str, optional): [description]. Defaults to None.
        """
        key = self.model.hash() if key is None else key
        if not getattr(self, "memory_cache", False):
            self.init_memory_cache()
        self.memory_cache[key] = results

    def set_disk_cache(self, results: Any, key: str = None) -> None:
        """Store result in disk cache with key matching model state.

        Args:
            results (Any): [description]
            key (str, optional): [description]. Defaults to None.
        """
        if not getattr(self, "disk_cache_location", False):
            self.init_disk_cache()
        disk_cache = shelve.open(str(self.disk_cache_location))
        key = self.model.hash() if key is None else key
        disk_cache[key] = results
        disk_cache.close()

    def set_cache(self, results: Any, key: str = None) -> bool:
        """Store result in disk and/or memory cache for key 'key', depending
        on whether `use_disk_cache` and `use_memory_cache` are True.

        Args:
            results (Any): [description]
            key (str, optional): [description]. Defaults to None.

        Returns:
            bool: True if cache was successfully set, else False
        """
        if self.use_memory_cache:
            self.set_memory_cache(results, key=key)
        if self.use_disk_cache:
            self.set_disk_cache(results, key=key)
        if self.use_memory_cache or self.use_disk_cache:
            return True
        return False

    def load_model(self) -> None:
        """Load the model into memory."""

    def set_attrs(self, **attrs) -> None:
        """Set model attributes on the backend."""

    def set_run_params(self, **run_params) -> None:
        """Set model attributes on the backend."""

    def backend_run(self) -> Any:
        """Check for cached results; then run the model if needed.

        Returns:
            Any: The result of running backend.
        """
        if self.use_memory_cache or self.use_disk_cache:
            key = self.model.hash()
        if self.use_memory_cache and self.get_memory_cache(key):
            return self.cache_to_results(self._results)
        if self.use_disk_cache and self.get_disk_cache(key):
            return self.cache_to_results(self._results)
        results = self._backend_run()
        if self.use_memory_cache:
            self.set_memory_cache(self.results_to_cache(results), key)
        if self.use_disk_cache:
            self.set_disk_cache(self.results_to_cache(results), key)
        return results

    def cache_to_results(self, cache: Any) -> Any:
        """A method to convert cache to some hypothetical Results object.

        Args:
            cache (Any): An object returned from .get_memory_cache() or .get_disk_cache().

        Returns:
            Any (optional): Either an object with the results of the simulation,
            or None (e.g. if cache_to_results() simply injects the results into some global object).
        """
        return cache

    def results_to_cache(self, results: Any) -> Any:
        """A method to convert the results from your model run
        into storable cache object (usually a simple dictionary or an array).

        Args:
            results (Any): An object returned from your ._backend_run().

        Returns:
            Any: The results in the format that's good for storing in cache.
        """
        return results

    def _backend_run(self) -> Any:
        """Run the model via the backend."""
        raise NotImplementedError("Each backend must implement '_backend_run'")

    def save_results(self, path: Union[str, Path] = ".") -> None:
        """Save results on disk.

        Args:
            path (Union[str, Path], optional): [description]. Defaults to '.'.
        """
        with open(path, "wb") as f:
            pickle.dump(self.results, f)


class BackendException(Exception):
    """Generic backend exception class."""


# Register the base class as a Backend just so that there is
# always something available.  This Backend won't do anything
# useful other than caching.
register_backends({None: Backend})
