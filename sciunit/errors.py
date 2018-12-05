"""
Exception classes for SciUnit
"""


class Error(Exception):
    """Base class for errors in sciunit's core."""
    pass


class ObservationError(Error):
    """Raised when an observation passed to a test is invalid."""
    pass


class ParametersError(Error):
    """Raised when params passed to a test are invalid."""
    pass


class CapabilityError(Error):
    """Error raised when a required capability is not
    provided by a model."""
    def __init__(self, model, capability, details=''):
        self.model = model
        self.capability = capability
        if details:
            details = ' (%s)' % details

        super(CapabilityError, self).__init__(
            "Model '%s' does not provide required capability: '%s'%s" %
            (model.name, capability.__name__, details))

    model = None
    """The model that does not have the capability."""

    capability = None
    """The capability that is not provided."""


class PredictionError(Error):
    """Raised when a tests's generate_prediction chokes on a model's method"""
    def __init__(self, model, method, **args):
        self.model = model
        self.method = method
        self.args = args

        super(PredictionError, self).__init__(
            ("During prediction, model '%s' could not successfully execute "
             "method '%s' with arguments %s") % (model.name, method, args))

    model = None
    """The model that does not have the capability."""

    argument = None
    """The argument that could not be handled."""


class InvalidScoreError(Error):
    """Error raised when a score is invalid."""
    pass


class BadParameterValueError(Error):
    """Error raised when a model parameter value is unreasonable."""
    def __init__(self, name, value):
        self.name = name
        self.value = value

        super(BadParameterValueError, self).__init__(
            "Parameter %s has unreasonable value of %s" % (name, value))
