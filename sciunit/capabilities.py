"""The base class for SciUnit capabilities.

By inheriting a capability class, a model tells the test that it implements
that capability and that all of its methods are safe to call.
The capability must then be implemented by the modeler (i.e. all of the
capabilty's methods must implemented in the model class).
"""

import inspect

from .base import SciUnit
from .errors import CapabilityNotImplementedError


class Capability(SciUnit):
    """Abstract base class for sciunit capabilities."""

    @classmethod
    def check(cls, model, require_extra=False):
        """Check whether the provided model has this capability.

        By default, uses isinstance.  If `require_extra`, also requires that an
        instance check be present in `model.extra_capability_checks`.
        """
        class_capable = isinstance(model, cls)

        f_name = model.extra_capability_checks.get(cls, None) \
            if model.extra_capability_checks is not None \
            else False

        if f_name:
            f = getattr(model, f_name)
            instance_capable = f()
        elif not require_extra:
            instance_capable = True
        else:
            instance_capable = False
        return class_capable and instance_capable

    def unimplemented(self, message=''):
        """Raise a `CapabilityNotImplementedError` with details."""
        from sciunit import Model
        capabilities = [obj for obj in self.__class__.mro() if issubclass(obj, Capability) and not issubclass(obj, Model)]
        model = self if isinstance(self, Model) else None
        capability = None if not capabilities else capabilities[0]
        print(model, capability)
        raise CapabilityNotImplementedError(model, capability, message)

    class __metaclass__(type):
        @property
        def name(cls):
            return cls.__name__

    def __str__(self):
        return self.name


class ProducesNumber(Capability):
    """An example capability for producing some generic number."""

    def produce_number(self):
        """Produce a number."""
        self.unimplemented()


class Runnable(Capability):
    """Capability for models that can be run, i.e. simulated."""

    def run(self, **run_params):
        """Run, i.e. simulate the model."""
        self.unimplemented()

    def set_run_params(self, **run_params):
        """Set parameters for the next run.

        Note these are parameters of the simulation itself, not the model.
        """
        self.unimplemented()

    def set_default_run_params(self, **default_run_params):
        """Set default parameters for all runs.

        Note these are parameters of the simulation itself, not the model.
        """
        self.unimplemented()
