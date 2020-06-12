"""Example SciUnit model classes."""

import random
from sciunit.models import Model
from sciunit.capabilities import ProducesNumber
from sciunit.utils import class_intern, method_cache
from sciunit.utils import method_memoize  # Decorator for caching of capability method results.
from typing import Union

class ConstModel(Model, ProducesNumber):
    """A model that always produces a constant number as output."""

    def __init__(self, constant: Union[int, float], name: str=None):
        self.constant = constant
        super(ConstModel, self).__init__(name=name, constant=constant)

    def produce_number(self) -> Union[int, float]:
        return self.constant


class UniformModel(Model, ProducesNumber):
    """A model that always produces a random uniformly distributed number.
    in [a,b] as output."""

    def __init__(self, a, b, name=None):
        self.a, self.b = a, b
        super(UniformModel, self).__init__(name=name, a=a, b=b)

    def produce_number(self) -> float:
        """Produece a number between `a` and `b`.

        Returns:
            float: The number between a and b.
        """
        return random.uniform(self.a, self.b)


################################################################
# Here are several examples of caching and sharing can be used
# to reduce the computational load of testing.
################################################################

class UniqueRandomNumberModel(Model, ProducesNumber):
    """An example model to ProducesNumber."""

    def produce_number(self) -> float:
        """Each call to this method will produce a different random number.

        Returns:
            float: A random number produced.
        """
        return random.random()


class RepeatedRandomNumberModel(Model, ProducesNumber):
    """An example model to demonstrate ProducesNumber with cypy.lazy."""

    @method_memoize
    def produce_number(self):
        """Each call to this method will produce the same random number as was returned in the first call, ensuring reproducibility and eliminating computational overhead.

        Returns:
            float: A random number produced.
        """
        return random.random()


@class_intern
class SharedModel(Model):
    """A model that, each time it is instantiated with the same parameters,
    will return the same instance at the same locaiton in memory.
    Attributes should not be set post-instantiation
    unless the goal is to set those attributes on all models of this class."""
    pass


class PersistentUniformModel(UniformModel):
    """TODO"""

    def run(self) -> None:
        self._x = random.uniform(self.a, self.b)

    def produce_number(self) -> float:
        return self._x


class CacheByInstancePersistentUniformModel(PersistentUniformModel):
    """TODO"""

    @method_cache(by='instance', method='run')
    def produce_number(self) -> float:
        return self._x


class CacheByValuePersistentUniformModel(PersistentUniformModel):
    """TODO"""

    @method_cache(by='value', method='run')
    def produce_number(self) -> float:
        return self._x
