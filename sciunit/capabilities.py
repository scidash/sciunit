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
    def check(cls, model, require_extra=False):
        """Check whether the provided model has this capability.

        By default, uses isinstance.  If `require_extra`, also requires that an
        instance check be present in `model.extra_capability_checks`.
        """
        class_capable = isinstance(model, cls)
        f_name = model.extra_capability_checks.get(cls, None)
        if f_name:
            f = getattr(model, f_name)
            instance_capable = f()
        elif not require_extra:
            instance_capable = True
        else:
            instance_capable = False
        return class_capable and instance_capable

    def unimplemented(self):
        """Raise a `NotImplementedError` with details."""
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
        """Produce a number."""
        raise NotImplementedError("Must implement produce_number.")
