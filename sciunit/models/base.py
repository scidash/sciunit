"""Base class for SciUnit models."""

import inspect
from fnmatch import fnmatchcase
from typing import Union

from sciunit.base import SciUnit
from sciunit.capabilities import Capability


class Model(SciUnit):
    """Abstract base class for sciunit models."""

    def __init__(self, name=None, **params):
        """Instantiate model."""
        if name is None:
            name = self.__class__.__name__
        self.name = name
        self.params = params
        super(Model, self).__init__()
        self.check_params()

    name = None
    """The name of the model. Defaults to the class name."""

    description = ""
    """A description of the model."""

    params = None
    """The parameters to the model (a dictionary).
    These distinguish one model of a class from another."""

    run_args = None
    """These are the run-time arguments for the model.
    Execution of run() should make use of these arguments."""

    extra_capability_checks = None
    """Optional extra checks of capabilities on a per-instance basis."""

    _backend = None
    """Optional model backend for executing some methods, e.g. simulations."""

    state_hide = ["results", "temp_dir", "_temp_dir", "stdout"]

    @classmethod
    def get_capabilities(cls) -> list:
        """List the model's capabilities."""
        capabilities = []
        for _cls in cls.mro():
            if (
                issubclass(_cls, Capability)
                and _cls is not Capability
                and not issubclass(_cls, Model)
            ):
                capabilities.append(_cls)
        return capabilities

    @property
    def capabilities(self) -> list:
        return self.__class__.get_capabilities()

    @property
    def failed_extra_capabilities(self) -> list:
        """Check to see if instance passes its `extra_capability_checks`."""
        failed = []
        for capability, f_name in self.extra_capability_checks.items():
            f = getattr(self, f_name)
            instance_capable = f()
            if isinstance(self, capability) and not instance_capable:
                failed.append(capability)
        return failed

    def describe(self) -> str:
        """Describe the model.

        Returns:
            str: The description of the model.
        """
        result = "No description available"
        if self.description:
            result = "%s" % self.description
        else:
            if self.__doc__:
                s = []
                s += [self.__doc__.strip().replace("\n", "").replace("    ", " ")]
                result = "\n".join(s)
        return result

    def curr_method(self, back: int = 0) -> str:
        """Return the name of the current method (calling this one).

        Args:
            back (int, optional): [description]. Defaults to 0.

        Returns:
            str: The name of the current method that calls this one.
        """
        return inspect.stack()[1 + back][3]

    def check_params(self) -> None:
        """Check model parameters to see if they are reasonable.

        For example, this method could check self.params to see if a particular
        value was within an acceptable range.  This should be implemented
        as needed by specific model classes.
        """

    def is_match(self, match: Union[str, "Model"]) -> bool:
        """Return whether this model is the same as `match`.

        Matches if the model is the same as or has the same name as `match`.

        Args:
            match (Union[str, 'Model']): [description]

        Returns:
            bool: Whether this model is the same as `match`.
        """
        result = False
        if self == match:
            result = True
        elif isinstance(match, str) and fnmatchcase(self.name, match):
            result = True  # Found by instance or name
        return result

    def __getattr__(self, attr):
        try:
            result = super(Model, self).__getattribute__(attr)
        except AttributeError:
            try:
                result = self._backend.__getattribute__(attr)
            except:
                raise AttributeError("Model %s has no attribute %s" % (self, attr))
        return result

    def __str__(self):
        """Return the model name."""
        return "%s" % self.name

    def __repr__(self):
        """Returns a representation of the model."""
        return "%s (%s)" % (self.name, self.__class__.__name__)
