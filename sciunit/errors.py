"""
Exception classes for SciUnit
"""

import inspect
import sciunit

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
    """Abstract error class for capabilities"""
    def __init__(self, model, capability, details=''):
        """
        model: a model instance
        capablity: a capability class
        """
        self.model = model
        self.capability = capability
        if details:
            details = ' (%s)' % details
        if self.action:
            msg = "Model '%s' does not %s required capability: '%s'%s" % \
                  (model.name, self.action, capability.__name__, details)
        super(CapabilityError, self).__init__(details)
    
    action = None
    """The action that has failed ('provide' or 'implement')"""
    
    model = None
    """The model instance that does not have the capability."""

    capability = None
    """The capability class that is not provided."""


class CapabilityNotProvidedError(CapabilityError):
    """Error raised when a required capability is not *provided* by a model.
    Do not use for capabilities provided but not implemented."""
    
    action = 'provide'

class CapabilityNotImplementedError(CapabilityError):
    """Error raised when a required capability is not *implemented* by a model.
    Do not use for capabilities that are not provided at all."""
    
    action = 'implement'


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
