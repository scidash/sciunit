"""
Exception classes for SciUnit
"""


import sciunit


class Error(Exception):
    """Base class for errors in sciunit's core."""


class ObservationError(Error):
    """Raised when an observation passed to a test is invalid."""


class ParametersError(Error):
    """Raised when params passed to a test are invalid."""


class CapabilityError(Error):
    """Abstract error class for capabilities"""

    def __init__(
        self,
        model: "sciunit.Model",
        capability: "sciunit.Capability",
        details: str = "",
    ):
        """A constructor.
        Args:
            model (Model): A sciunit model instance.
            capability (Capability): a capability class.
            details (str, optional): Details of the error information. Defaults to ''.
        """
        self.model = model
        self.capability = capability
        if details:
            details = " (%s)" % details
        if self.action:
            msg = "Model '%s' does not %s required capability: '%s'%s" % (
                model.name,
                self.action,
                capability.__name__,
                details,
            )
        super(CapabilityError, self).__init__(details)

    action = None
    """The action that has failed ('provide' or 'implement')."""

    model = None
    """The model instance that does not have the capability."""

    capability = None
    """The capability class that is not provided."""


class CapabilityNotProvidedError(CapabilityError):
    """Error raised when a required capability is not *provided* by a model.
    Do not use for capabilities provided but not implemented."""

    action = "provide"


class CapabilityNotImplementedError(CapabilityError):
    """Error raised when a required capability is not *implemented* by a model.
    Do not use for capabilities that are not provided at all."""

    action = "implement"


class PredictionError(Error):
    """Raised when a tests's generate_prediction chokes on a model's method."""

    def __init__(self, model: "sciunit.Model", method: str, **args):
        """Constructor of PredictionError object.

        Args:
            model (Model): A sciunit Model.
            method (str): The method that caused this error.
        """
        self.model = model
        self.method = method
        self.args = args

        super(PredictionError, self).__init__(
            (
                "During prediction, model '%s' could not successfully execute "
                "method '%s' with arguments %s"
            )
            % (model.name, method, args)
        )

    model = None
    """The model that does not have the capability."""

    argument = None
    """The argument that could not be handled."""


class InvalidScoreError(Error):
    """Error raised when a score is invalid."""


class BadParameterValueError(Error):
    """Error raised when a model parameter value is unreasonable."""

    def __init__(self, name: str, value: int):
        """Constructor of BadParameterValueError object.

        Args:
            name (str): Name of the parameter that caused this error.
            value (int): The value of the parameter.
        """
        self.name = name
        self.value = value

        super(BadParameterValueError, self).__init__(
            "Parameter %s has unreasonable value of %s" % (name, value)
        )
