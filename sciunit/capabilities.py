"""The base class for SciUnit capabilities.

By inheriting a capability class, a model tells the test that it implements
that capability and that all of its methods are safe to call.
The capability must then be implemented by the modeler (i.e. all of the
capabilty's methods must implemented in the model class).
"""

import inspect

from .base import SciUnit


class Capability(SciUnit):
    """Abstract base class for sciunit capabilities."""

    @classmethod
    def check(cls, model):
        """Checks whether the provided model has this capability.
        By default, uses isinstance.
        """
        class_capable = isinstance(model, cls)
        f = model.extra_capability_checks.get(cls, lambda: True)
        instance_capable = f()
        return class_capable and instance_capable

    def unimplemented(self):
        raise NotImplementedError(("The method %s promised by capability %s "
                                   "is not implemented") %
                                  (inspect.stack()[1][3], self.name))

    class __metaclass__(type):
        @property
        def name(cls):
            return cls.__name__


class ProducesNumber(Capability):
    """An example capability for producing some generic number."""

    def produce_number(self):
        raise NotImplementedError("Must implement produce_number.")
