"""Cerberus validator classes for SciUnit."""

import inspect

import quantities as pq
from cerberus import TypeDefinition, Validator
from typing import Any

def register_type(cls, name: str) -> None:
    """Register `name` as a type to validate as an instance of class `cls`.

    Args:
        cls: a class
        name (str): the name to be registered.
    """
    x = TypeDefinition(name, (cls,), ())
    Validator.types_mapping[name] = x
    

def register_quantity(quantity: pq.Quantity, name: str) -> None:
    """Register `name` as a type to validate as an instance of the class of `quantity`.

    Args:
        quantity (pq.Quantity): a quantity.
        name (str): the name to be registered.
    """

    x = TypeDefinition(name, (quantity.__class__,), ())
    Validator.types_mapping[name] = x


class ObservationValidator(Validator):
    """Cerberus validator class for observations.

    Attributes:
        test (Test): A sciunit test instance to be validated.
        _error (str, str): The error that happens during the validating process.
    """

    def __init__(self, *args, **kwargs):
        """ Constructor of ObservationValidator.

        Must pass `test` as a keyword argument. Cannot be a positional argument without modifications to cerberus.

        Raises:
            Exception: "Observation validator constructor must have a `test` keyword argument."
        """

        try:
            self.test = kwargs['test']
        except KeyError:
            raise Exception(("Observation validator constructor must have "
                             "a `test` keyword argument"))
        super(ObservationValidator, self).__init__(*args, **kwargs)
        register_type(pq.quantity.Quantity, 'quantity')

    def _validate_iterable(self, is_iterable: bool, key: str, value: Any) -> None:
        """Validate fields with `iterable` key in schema set to True
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if is_iterable:
            try:
                iter(value)
            except TypeError:
                self._error(key, "Must be iterable (e.g. a list or array)")


    def _validate_units(self, has_units: bool, key: str, value: Any) -> None:
        """Validate fields with `units` key in schema set to True.
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if has_units:
            if isinstance(self.test.units, dict):
                required_units = self.test.units[key]
            else:
                required_units = self.test.units
            if not isinstance(value, pq.quantity.Quantity):
                self._error(key, "Must be a python quantity")
            provided_units = value.simplified.units
            if not isinstance(required_units, pq.Dimensionless):
                required_units = required_units.simplified.units
            if not required_units == provided_units:
                self._error(key,
                            "Must have units of '%s'" % self.test.units.name)


class ParametersValidator(Validator):
    """Cerberus validator class for observations.

    Attributes:
        units_type ([type]): The type of Python quantity's unit. 
        _error (str, str): value is not a Python quantity instance.
    """

    # doc is needed here
    units_map = {'time': 's', 'voltage': 'V', 'current': 'A'}

    def validate_quantity(self, value: pq.quantity.Quantity) -> None:
        """Validate that the value is of the `Quantity` type.

        Args:
            value (pq.quantity.Quantity): The Quantity instance to be validated.
        """
        if not isinstance(value, pq.quantity.Quantity):
            self._error('%s' % value, "Must be a Python quantity.")

    def validate_units(self, value: pq.quantity.Quantity) -> bool:
        """Validate units, assuming that it was called by _validate_type_*.

        Args:
            value (pq.quantity.Quantity): A python quantity instance.

        Returns:
            bool: Whether it is valid.
        """
        self.validate_quantity(value)
        self.units_type = inspect.stack()[1][3].split('_')[-1]
        assert self.units_type, ("`validate_units` should not be called "
                                 "directly. It should be called by a "
                                 "_validate_type_* methods that sets "
                                 "`units_type`")
        units = getattr(pq, self.units_map[self.units_type])
        if not value.simplified.units == units:
            self._error('%s' % value,
                        "Must have dimensions of %s." % self.units_type)
        return True

    def _validate_type_time(self, value: pq.quantity.Quantity) -> bool:
        """Validate fields requiring `units` of seconds.

        Args:
            value (pq.quantity.Quantity): A python quantity instance.

        Returns:
            bool: Whether it is valid.
        """
        return self.validate_units(value)

    def _validate_type_voltage(self, value: pq.quantity.Quantity) -> bool:
        """Validate fields requiring `units` of volts.

        Args:
            value (pq.quantity.Quantity): A python quantity instance.

        Returns:
            bool: Whether it is valid.
        """
        return self.validate_units(value)

    def _validate_type_current(self, value: pq.quantity.Quantity) -> bool:
        """Validate fields requiring `units` of amps.

        Args:
            value (pq.quantity.Quantity): A python quantity instance.

        Returns:
            bool: Whether it is valid.
        """
        return self.validate_units(value)
