"""Runnable model."""

from .base import Model
import sciunit.capabilities as cap
from .backends import available_backends


class RunnableModel(Model,
                    cap.Runnable):
    """A model which can be run to produce simulation results"""

    def __init__(self,
                 name,  # Name of the model
                 backend=None,  # Backend to run the models
                 attrs=None,  # Optional dictionary of model attributes
                 ):
        super(RunnableModel, self).__init__(name=name)
        self.skip_run = False  # Backend can use this to skip simulation
        self.run_params = {}  # Should be reset between tests
        self.print_run_params = False  # Print the run parameters with each run
        self.default_run_params = {}  # Should be applied to all tests
        self.unpicklable = []  # Model attributes which cannot be pickled
        if attrs and not isinstance(attrs, dict):
            raise TypeError("Model 'attrs' must be a dictionary.")
        self.attrs = attrs if attrs else {}
        self.set_backend(backend)
        self.use_default_run_params()

    def get_backend(self):
        """Return the simulation backend."""
        return self._backend

    def set_backend(self, backend):
        """Set the simulation backend."""
        if isinstance(backend, str):
            name = backend
            args = []
            kwargs = {}
        elif isinstance(backend, (tuple, list)):
            name = ''
            args = []
            kwargs = {}
            for i in range(len(backend)):
                if i == 0:
                    name = backend[i]
                else:
                    if isinstance(backend[i], dict):
                        kwargs.update(backend[i])
                    else:
                        args += backend[i]
        else:
            raise TypeError("Backend must be string, tuple, or list")
        if name in available_backends:
            self.backend = name
            self._backend = available_backends[name]()
        elif name is None:
            # The base class should not be called.
            raise Exception(("A backend (e.g. 'jNeuroML' or 'NEURON') "
                             "must be selected"))
        else:
            raise Exception("Backend %s not found in backends.py"
                            % name)
        self._backend.model = self
        self._backend.init_backend(*args, **kwargs)

    def run(self, **run_params):
        """Run the simulation (or lookup the results in the cache)."""
        self.use_default_run_params()
        self.set_run_params(**run_params)
        if self.print_run_params:
            print("Run Params:", self.run_params)
        self.results = self._backend.backend_run()

    def set_attrs(self, **attrs):
        """Set model attributes, e.g. input resistance of a cell."""
        self.attrs.update(attrs)
        self._backend.set_attrs(**attrs)

    def set_run_params(self, **run_params):
        """Set run-time parameters, e.g. the somatic current to inject."""
        self.run_params.update(run_params)
        self.check_run_params()
        self._backend.set_run_params(**run_params)

    def check_run_params(self):
        """Check if run parameters are reasonable for this model class.

        Raise a sciunit.BadParameterValueError if any of them are not.
        """
        pass

    def reset_run_params(self):
        self.run_params = {}

    def set_default_run_params(self, **params):
        self.default_run_params.update(params)

    def use_default_run_params(self):
        for key, value in self.default_run_params.items():
            if key not in self.run_params:
                self.set_run_params(**{key: value})

    def reset_default_run_params(self):
        self.default_run_params = {}

    @property
    def state(self):
        return self._state(keys=['name', 'url', 'attrs', 'run_params',
                                 'backend'])

    def __del__(self):
        if hasattr(self, 'temp_dir'):
            self.temp_dir.cleanup()   # Delete the temporary directory
            s = super(RunnableModel, self)
            if hasattr(s, '__del__'):
                s.__del__()
